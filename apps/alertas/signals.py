from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.equipos.models import EventoConexion
from apps.ocupacion.models import EventoOcupacion
from .models import Alerta

# Horario institucional (HU-24). Configurable en settings:
HORARIO_INICIO = getattr(settings, 'HORARIO_INICIO', 6)
HORARIO_FIN    = getattr(settings, 'HORARIO_FIN', 22)


# ── HU-24 — Alerta de movimiento fuera de horario ─────────────────────────────
@receiver(post_save, sender=EventoOcupacion)
def alerta_movimiento_inusual(sender, instance, created, **kwargs):
    """
    Genera alerta crítica si se detecta ocupación fuera del horario institucional.
    IMPORTANTE: se usa la hora LOCAL (America/Guayaquil), no la UTC almacenada.
    """
    if created and instance.estado == 'ocupado':
        hora_local = timezone.localtime(instance.timestamp)
        hora = hora_local.hour
        if hora >= HORARIO_FIN or hora < HORARIO_INICIO:
            ctype = ContentType.objects.get_for_model(instance.dispositivo)
            Alerta.objects.create(
                tipo='movimiento',
                descripcion=(
                    f'Movimiento fuera de horario detectado en '
                    f'{instance.dispositivo.laboratorio.nombre} '
                    f'(Dispositivo: {instance.dispositivo.identificador}) '
                    f'a las {hora_local.strftime("%H:%M")}.'
                ),
                nivel='critico',
                content_type=ctype,
                object_id=instance.dispositivo.id
            )


# ── Alerta de desconexión de un EQUIPO (PC) ──────────────────────────────────
@receiver(post_save, sender=EventoConexion)
def alerta_desconexion_equipo(sender, instance, created, **kwargs):
    """
    Genera alerta crítica cuando un equipo PC se desconecta inesperadamente.
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

# NOTA: la alerta de desconexión del ESP32 (HU-25) y la de equipo activo sin
# ocupación (HU-26) se generan en el scheduler (apps/automatizacion/scheduler.py).