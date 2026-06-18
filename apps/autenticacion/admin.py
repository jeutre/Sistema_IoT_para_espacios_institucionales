from django.contrib import admin
from .models import SesionUsuario


@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    list_display  = ['usuario', 'inicio', 'ip', 'activa']
    list_filter   = ['activa']
    search_fields = ['usuario__username']
    ordering      = ['-inicio']