from django.db import models
from apps.dispositivos.models import Dispositivo

class Comando(models.Model):
    TIPO_ACCION_CHOICES = [
        ('encender_aire', 'Encender Aire Acondicionado'),
        ('apagar_aire', 'Apagar Aire Acondicionado'),
        ('encender_luces', 'Encender Luces'),
        ('apagar_luces', 'Apagar Luces'),
        ('reiniciar', 'Reiniciar Dispositivo'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('ejecutado', 'Ejecutado'),
        ('fallido', 'Fallido'),
    ]

    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='comandos')
    tipo_accion = models.CharField(max_length=50, choices=TIPO_ACCION_CHOICES)
    estado      = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    creado_en   = models.DateTimeField(auto_now_add=True)
    ejecutado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Comando'
        verbose_name_plural = 'Comandos'

    def __str__(self):
        return f"{self.get_tipo_accion_display()} -> {self.dispositivo.identificador} ({self.estado})"
