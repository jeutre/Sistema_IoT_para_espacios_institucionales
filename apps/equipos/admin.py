from django.contrib import admin
from .models import Equipo, EventoConexion


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'laboratorio', 'ip', 'mac', 'activo']
    list_filter   = ['activo', 'laboratorio']
    search_fields = ['nombre', 'ip', 'mac']

@admin.register(EventoConexion)
class EventoConexionAdmin(admin.ModelAdmin):
    list_display  = ['equipo', 'tipo', 'registrado_en']
    list_filter   = ['tipo', 'equipo']
    search_fields = ['equipo__nombre']
    ordering      = ['-registrado_en']
    
    