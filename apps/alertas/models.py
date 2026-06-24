from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Alerta(models.Model):
    NIVELES_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('critico', 'Crítico'),
    ]

    TIPO_CHOICES = [
        ('desconexion', 'Desconexión de Equipo'),
        ('movimiento', 'Movimiento Fuera de Horario'),
        ('error_sistema', 'Error del Sistema'),
    ]

    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    nivel       = models.CharField(max_length=10, choices=NIVELES_CHOICES, default='medio')
    leida       = models.BooleanField(default=False)
    creado_en   = models.DateTimeField(auto_now_add=True)

    # Generic relation to tie this alert to Dispositivo, Equipo, etc.
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id      = models.PositiveIntegerField(null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'

    def __str__(self):
        return f"[{self.get_nivel_display()}] {self.get_tipo_display()} - {self.creado_en}"
