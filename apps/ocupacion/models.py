from django.db import models
from apps.dispositivos.models import Dispositivo


class EventoOcupacion(models.Model):
    ESTADO_CHOICES = [
        ('ocupado', 'Aula Ocupada'),
        ('vacio',   'Aula Vacía'),
    ]

    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='eventos')
    estado      = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-registrado_en']
        verbose_name = 'Evento de ocupación'
        verbose_name_plural = 'Eventos de ocupación'

    def __str__(self):
        return f'{self.dispositivo.identificador} — {self.estado} — {self.registrado_en}'