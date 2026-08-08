from django.contrib import admin
from .models import Dispositivo, HistorialComunicacion


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ['identificador', 'tipo', 'ip', 'estado', 'laboratorio', 'ultima_conexion']
    list_filter = ['tipo', 'estado', 'laboratorio']
    search_fields = ['identificador', 'ip']


@admin.register(HistorialComunicacion)
class HistorialComunicacionAdmin(admin.ModelAdmin):
    list_display = ['dispositivo', 'tipo_evento', 'exitoso', 'recibido_en']
    list_filter = ['tipo_evento', 'exitoso']
    search_fields = ['dispositivo__identificador']