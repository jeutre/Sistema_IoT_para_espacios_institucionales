from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.equipos.models import EventoConexion
from apps.ocupacion.models import EventoOcupacion
from .models import Alerta

@receiver(post_save, sender=EventoConexion)
def alerta_desconexion_equipo(sender, instance, created, **kwargs):
    if created and instance.tipo == 'desconexion':
        ctype = ContentType.objects.get_for_model(instance.equipo)
        Alerta.objects.create(
            tipo='desconexion',
            descripcion=f'El equipo {instance.equipo.nombre} ({instance.equipo.ip}) se ha desconectado inesperadamente.',
            nivel='critico',
            content_type=ctype,
            object_id=instance.equipo.id
        )

@receiver(post_save, sender=EventoOcupacion)
def alerta_movimiento_inusual(sender, instance, created, **kwargs):
    # Lógica simplificada: si detecta movimiento entre las 22:00 y las 06:00
    if created and instance.estado == 'ocupado':
        hora = instance.registrado_en.hour
        if hora >= 22 or hora < 6:
            ctype = ContentType.objects.get_for_model(instance.dispositivo)
            Alerta.objects.create(
                tipo='movimiento',
                descripcion=f'Movimiento inusual detectado fuera de horario en {instance.dispositivo.laboratorio.nombre} (Dispositivo: {instance.dispositivo.identificador}).',
                nivel='critico',
                content_type=ctype,
                object_id=instance.dispositivo.id
            )
