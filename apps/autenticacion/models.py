from django.db import models
from django.contrib.auth.models import User


class SesionUsuario(models.Model):
    usuario    = models.ForeignKey(User, on_delete=models.CASCADE)
    inicio     = models.DateTimeField(auto_now_add=True)
    ip         = models.GenericIPAddressField(null=True, blank=True)
    activa     = models.BooleanField(default=True)

    class Meta:
        ordering = ['-inicio']
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'

    def __str__(self):
        return f'{self.usuario.username} - {self.inicio}'