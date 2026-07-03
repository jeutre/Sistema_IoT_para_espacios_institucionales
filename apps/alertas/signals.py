from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.equipos.models import EventoConexion
from apps.ocupacion.models import EventoOcupacion
from apps.dispositivos.models import Dispositivo, HistorialComunicacion
from .models import Alerta


# ── HU-24 — Alerta movimiento fuera de horario ────────────────────────────────
@receiver(post_save, sender=EventoOcupacion)
def alerta_movimiento_inusual(sender, instance, created, **kwargs):
    """
    Genera alerta crítica si hay movimiento entre las 22:00 y las 06:00.
    Horario institucional configurable en el futuro desde HU-28.
    """
    if created and instance.estado == 'ocupado':
        hora = instance.registrado_en.hour
        if hora >= 22 or hora < 6:
            ctype = ContentType.objects.get_for_model(instance.dispositivo)
            Alerta.objects.create(
                tipo='movimiento',
                descripcion=(
                    f'Movimiento fuera de horario detectado en '
                    f'{instance.dispositivo.laboratorio.nombre} '
                    f'(Dispositivo: {instance.dispositivo.identificador}) '
                    f'a las {instance.registrado_en.strftime("%H:%M")}.'
                ),
                nivel='critico',
                content_type=ctype,
                object_id=instance.dispositivo.id
            )


# ── HU-24 / HU-26 — Alerta equipo activo sin ocupación ───────────────────────
@receiver(post_save, sender=EventoConexion)
def alerta_desconexion_equipo(sender, instance, created, **kwargs):
    """
    Genera alerta crítica cuando un equipo PC se desconecta inesperadamente.
    También dispara el proceso de suspensión/apagado automático (HU-26).
    """
    if created and instance.tipo == 'desconexion':
        ctype = ContentType.objects.get_for_model(instance.equipo)
        Alerta.objects.create(
            tipo='desconexion',
            descripcion=(
                f'El equipo {instance.equipo.nombre} ({instance.equipo.ip}) '
                f'se ha desconectado inesperadamente.'
            ),
            nivel='critico',
            content_type=ctype,
            object_id=instance.equipo.id
        )


# ── HU-25 — Alerta desconexión ESP32 ─────────────────────────────────────────
@receiver(post_save, sender=HistorialComunicacion)
def verificar_timeout_esp32(sender, instance, created, **kwargs):
    """
    Cada vez que el ESP32 envía un mensaje, este signal verifica si hay
    OTROS dispositivos que no han comunicado en más de 5 minutos y genera
    alerta por cada uno.

    Lógica: si el ESP32 A acaba de comunicar pero el ESP32 B lleva más de
    5 minutos sin comunicar, B probablemente está caído.

    El umbral de 5 minutos es conservador para un laboratorio. Ajustar
    según la frecuencia real de envío del ESP32 (heartbeat).
    """
    if not created:
        return

    UMBRAL_MINUTOS = 5
    ahora          = timezone.now()
    limite         = ahora - timezone.timedelta(minutes=UMBRAL_MINUTOS)

    # Busca dispositivos que NO han comunicado en el umbral de tiempo
    # y que actualmente están marcados como conectados (estado inconsistente)
    dispositivos_sin_comunicar = Dispositivo.objects.filter(
        ultima_conexion__lt=limite,
        estado='conectado'
    ).exclude(id=instance.dispositivo.id)  # Excluye el que acaba de comunicar

    for dispositivo in dispositivos_sin_comunicar:
        # Actualiza estado a desconectado
        dispositivo.estado = 'desconectado'
        dispositivo.save()

        # Verifica que no exista ya una alerta reciente para no spammear
        alerta_reciente = Alerta.objects.filter(
            tipo='desconexion',
            object_id=dispositivo.id,
            creado_en__gte=limite
        ).exists()

        if not alerta_reciente:
            ctype = ContentType.objects.get_for_model(dispositivo)
            minutos_sin_comunicar = int(
                (ahora - dispositivo.ultima_conexion).total_seconds() // 60
            )
            Alerta.objects.create(
                tipo='desconexion',
                descripcion=(
                    f'El ESP32 {dispositivo.identificador} '
                    f'({dispositivo.laboratorio.nombre}) lleva '
                    f'{minutos_sin_comunicar} minutos sin comunicarse. '
                    f'Última comunicación: '
                    f'{dispositivo.ultima_conexion.strftime("%d/%m/%Y %H:%M")}.'
                ),
                nivel='critico',
                content_type=ctype,
                object_id=dispositivo.id
            )