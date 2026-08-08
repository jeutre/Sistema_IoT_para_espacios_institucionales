from django.db import models
from django.contrib.auth.models import User


class SesionUsuario(models.Model):
    """HU-01 — Registro de cada inicio de sesión del administrador."""

    usuario       = models.ForeignKey(User, on_delete=models.CASCADE)
    inicio        = models.DateTimeField(auto_now_add=True)
    fecha_fin     = models.DateTimeField(null=True, blank=True)
    ip            = models.GenericIPAddressField(null=True, blank=True)
    user_agent    = models.CharField(max_length=255, blank=True, default='')
    token_refresh = models.CharField(max_length=255, blank=True, default='')
    activa        = models.BooleanField(default=True)

    class Meta:
        ordering = ['-inicio']
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'

    def __str__(self):
        return f'{self.usuario.username} - {self.inicio}'