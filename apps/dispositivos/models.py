from django.db import models
from apps.laboratorio.models import Laboratorio


class Dispositivo(models.Model):
    TIPO_CHOICES = [
        ('esp32', 'ESP32'),
        ('relay', 'Modulo Relay'),
        ('pir',   'Sensor PIR'),
    ]
    ESTADO_CHOICES = [
        ('conectado',    'Conectado'),
        ('desconectado', 'Desconectado'),
    ]

    laboratorio     = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='dispositivos')
    identificador   = models.CharField(max_length=100, unique=True)
    tipo            = models.CharField(max_length=20, choices=TIPO_CHOICES, default='esp32')
    mac_address     = models.CharField(max_length=17, unique=True, blank=True, null=True)
    ip              = models.GenericIPAddressField()
    api_key         = models.CharField(max_length=100, blank=True, default='')
    estado          = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='desconectado')
    ultima_conexion = models.DateTimeField(null=True, blank=True)
    firmware_version = models.CharField(max_length=20, blank=True, default='1.0.0')
    creado_en       = models.DateTimeField(auto_now_add=True)
    actualizado_en  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['identificador']
        verbose_name = 'Dispositivo ESP32'
        verbose_name_plural = 'Dispositivos ESP32'

    def __str__(self):
        return f'{self.identificador} - {self.laboratorio.nombre}'

    @property
    def esta_conectado(self):
        if not self.ultima_conexion:
            return False
        from django.utils import timezone
        return (timezone.now() - self.ultima_conexion).total_seconds() <= 120


class HistorialComunicacion(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('heartbeat', 'Heartbeat'),
        ('pir_dato',  'Dato PIR'),
        ('comando',   'Comando enviado'),
        ('respuesta', 'Respuesta recibida'),
        ('error',     'Error'),
    ]

    dispositivo   = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='historial')
    tipo_evento   = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, default='heartbeat')
    mensaje       = models.TextField(blank=True, default='')
    datos         = models.JSONField(default=dict, blank=True)
    exitoso       = models.BooleanField(default=True)
    recibido_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recibido_en']
        verbose_name = 'Historial de comunicacion'

    def __str__(self):
        return f'{self.dispositivo.identificador} - {self.recibido_en}'