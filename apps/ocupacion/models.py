from django.db import models
from django.conf import settings
from apps.dispositivos.models import Dispositivo


class EventoOcupacion(models.Model):
    """HU-09 — Cada dato recibido del sensor PIR"""

    class Estado(models.TextChoices):
        OCUPADO = 'ocupado', 'Ocupado'
        VACIO = 'vacio', 'Vacío'

    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.CASCADE,
        related_name='eventos_ocupacion',
    )
    estado = models.CharField(max_length=10, choices=Estado.choices)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ocupacion_evento_ocupacion'
        verbose_name = 'Evento de Ocupación'
        verbose_name_plural = 'Eventos de Ocupación'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.dispositivo.identificador}: {self.estado} @ {self.timestamp}"