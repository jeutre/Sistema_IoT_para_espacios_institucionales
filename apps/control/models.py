from django.db import models
from apps.dispositivos.models import Dispositivo
from apps.equipos.models import Equipo


class Comando(models.Model):
    TIPO_ACCION_CHOICES = [
        # Acciones sobre PCs vía agente Windows (HU-19, HU-20)
        ('suspender_equipo', 'Suspender Equipo'),
        ('apagar_equipo',    'Apagar Equipo'),
        # Acciones sobre relay del ESP32 (HU-20B, HU-29, HU-30)
        ('encender_relay',   'Encender por Relay'),
        ('encender_luces',   'Encender Iluminación'),
        ('apagar_luces',     'Apagar Iluminación'),
    ]

    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente'),
        ('ejecutado',  'Ejecutado'),
        ('fallido',    'Fallido'),
    ]

    # Dispositivo ESP32 — para comandos de relay/luces
    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.CASCADE,
        related_name='comandos',
        null=True, blank=True
    )

    # Equipo PC — para comandos de suspender/apagar (HU-19, HU-20)
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='comandos',
        null=True, blank=True
    )

    tipo_accion       = models.CharField(max_length=50, choices=TIPO_ACCION_CHOICES)
    estado            = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    ip_equipo_destino = models.GenericIPAddressField(null=True, blank=True)
    resultado         = models.TextField(null=True, blank=True)  # respuesta del agente
    creado_en         = models.DateTimeField(auto_now_add=True)
    ejecutado_en      = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Comando'
        verbose_name_plural = 'Comandos'

    def __str__(self):
        destino = self.equipo.nombre if self.equipo else self.dispositivo.identificador
        return f"{self.get_tipo_accion_display()} → {destino} ({self.estado})"