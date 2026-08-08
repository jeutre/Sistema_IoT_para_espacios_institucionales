from django.db import models
from django.core.validators import MinValueValidator


class Laboratorio(models.Model):
    """HU-03/04/05 — Laboratorio piloto"""

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'
        MANTENIMIENTO = 'mantenimiento', 'Mantenimiento'

    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200)
    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Número de equipos del laboratorio',
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    horario_apertura = models.TimeField(default='07:00')
    horario_cierre = models.TimeField(default='21:00')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'laboratorio_laboratorio'
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.ubicacion})"