from django.db import models
from django.core.validators import RegexValidator
from apps.laboratorio.models import Laboratorio


class Equipo(models.Model):
    ESTADO_CHOICES = [
        ('activo',     'Activo'),
        ('inactivo',   'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]

    nombre           = models.CharField(max_length=100)
    laboratorio      = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='equipos')
    ip               = models.GenericIPAddressField(verbose_name='Direccion IPv4')
    mac              = models.CharField(
        max_length=17, unique=True, verbose_name='Direccion MAC',
        validators=[RegexValidator(
            regex=r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$',
            message='Formato MAC invalido. Use XX:XX:XX:XX:XX:XX',
        )]
    )
    activo           = models.BooleanField(default=True, help_text='Equipo habilitado en el sistema')
    estado_conexion  = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='inactivo')
    ultima_actividad = models.DateTimeField(null=True, blank=True)
    ultimo_ping      = models.DateTimeField(null=True, blank=True)
    posicion_fisica  = models.CharField(max_length=20, blank=True)
    tiene_relay      = models.BooleanField(default=False)
    relay_gpio       = models.PositiveSmallIntegerField(null=True, blank=True)
    consumo_watts    = models.FloatField(default=250.0)
    creado_en        = models.DateTimeField(auto_now_add=True)
    actualizado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipos_equipo'
        ordering = ['laboratorio', 'nombre']
        unique_together = [['laboratorio', 'ip']]

    def __str__(self):
        return f"{self.nombre} ({self.ip})"

    @property
    def minutos_inactivo(self):
        if self.ultima_actividad:
            from django.utils import timezone
            return (timezone.now() - self.ultima_actividad).total_seconds() / 60
        return None


class EventoConexion(models.Model):
    TIPO_CHOICES = [
        ('conexion',    'Conexion'),
        ('desconexion', 'Desconexion'),
        ('suspension',  'Suspension'),
        ('apagado',     'Apagado'),
        ('encendido',   'Encendido'),
    ]

    equipo        = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='eventos_conexion')
    tipo          = models.CharField(max_length=20, choices=TIPO_CHOICES)
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'equipos_evento_conexion'
        ordering = ['-registrado_en']

    def __str__(self):
        return f"{self.equipo.nombre}: {self.tipo} @ {self.registrado_en}"