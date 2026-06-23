from django.db import models
from django.utils import timezone
from apps.laboratorio.models import Laboratorio


class Equipo(models.Model):
    ESTADO_CHOICES = [
        ('activo',   'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    laboratorio      = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='equipos')
    nombre           = models.CharField(max_length=100)
    ip               = models.GenericIPAddressField(unique=True)
    mac              = models.CharField(max_length=17, unique=True)
    activo           = models.BooleanField(default=True)
    creado_en        = models.DateTimeField(auto_now_add=True)

    # Campos para HU-14, HU-15, HU-16
    estado_conexion  = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='inactivo')
    ultimo_ping      = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return f'{self.nombre} — {self.ip}'

    @property
    def minutos_inactivo(self):
        """
        Calcula hace cuánto no responde el equipo. (HU-16)
        Devuelve None si nunca ha hecho ping o si está activo.
        """
        if not self.ultimo_ping or self.estado_conexion == 'activo':
            return None
        delta = timezone.now() - self.ultimo_ping
        return int(delta.total_seconds() // 60)


class EventoConexion(models.Model):
    """
    Registra cada CAMBIO de estado de un equipo (HU-17).
    No guarda cada ping, solo cuando el estado realmente cambia
    (de activo a inactivo o viceversa).
    """
    TIPO_CHOICES = [
        ('conexion',    'Conexión'),
        ('desconexion', 'Desconexión'),
    ]

    equipo        = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='eventos_conexion')
    tipo          = models.CharField(max_length=12, choices=TIPO_CHOICES)
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-registrado_en']
        verbose_name = 'Evento de conexión'
        verbose_name_plural = 'Eventos de conexión'

    def __str__(self):
        return f'{self.equipo.nombre} — {self.tipo} — {self.registrado_en}'