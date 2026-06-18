from django.db import models
from apps.laboratorio.models import Laboratorio


class Equipo(models.Model):
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='equipos')
    nombre      = models.CharField(max_length=100)
    ip          = models.GenericIPAddressField(unique=True)
    mac         = models.CharField(max_length=17, unique=True)
    activo      = models.BooleanField(default=True)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return f'{self.nombre} — {self.ip}'
