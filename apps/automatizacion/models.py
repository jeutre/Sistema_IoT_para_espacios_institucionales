from django.db import models

class ReglaAutomatizacion(models.Model):
    CONDICION_CHOICES = [
        ('inactividad_minutos', 'Minutos sin movimiento (PIR)'),
    ]

    nombre = models.CharField(max_length=100)
    condicion = models.CharField(max_length=50, choices=CONDICION_CHOICES)
    valor_umbral = models.IntegerField(help_text="Ej: 30 (minutos)")
    accion_a_ejecutar = models.CharField(max_length=50, help_text="Ej: apagar_aire, apagar_luces")
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Regla de Automatización'
        verbose_name_plural = 'Reglas de Automatización'

    def __str__(self):
        return f"{self.nombre} ({'Activa' if self.activa else 'Inactiva'})"
