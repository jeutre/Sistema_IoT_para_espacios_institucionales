from django.contrib import admin
from .models import Dispositivo, HistorialComunicacion


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display  = ['identificador', 'laboratorio', 'ip', 'estado', 'ultima_conexion']
    list_filter   = ['estado', 'laboratorio']
    search_fields = ['identificador', 'ip']


@admin.register(HistorialComunicacion)
class HistorialComunicacionAdmin(admin.ModelAdmin):
    list_display  = ['dispositivo', 'mensaje', 'recibido_en']
    list_filter   = ['dispositivo']
    search_fields = ['mensaje']