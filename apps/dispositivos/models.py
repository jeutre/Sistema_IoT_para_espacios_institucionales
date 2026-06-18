from django.db import models
from apps.laboratorio.models import Laboratorio


class Dispositivo(models.Model):
    ESTADO_CHOICES = [
        ('conectado',    'Conectado'),
        ('desconectado', 'Desconectado'),
    ]

    laboratorio       = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='dispositivos')
    identificador     = models.CharField(max_length=100, unique=True)
    ip                = models.GenericIPAddressField()
    estado            = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='desconectado')
    ultima_conexion   = models.DateTimeField(null=True, blank=True)
    creado_en         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['identificador']
        verbose_name = 'Dispositivo ESP32'
        verbose_name_plural = 'Dispositivos ESP32'

    def __str__(self):
        return f'{self.identificador} — {self.laboratorio.nombre}'


class HistorialComunicacion(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='historial')
    mensaje     = models.TextField()
    recibido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recibido_en']
        verbose_name = 'Historial de comunicación'

    def __str__(self):
        return f'{self.dispositivo.identificador} — {self.recibido_en}'