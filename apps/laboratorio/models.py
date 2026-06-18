from django.db import models
 
 
class Laboratorio(models.Model):
    nombre    = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)
    capacidad = models.PositiveIntegerField()
    activo    = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'
 
    def __str__(self):
        return self.nombre