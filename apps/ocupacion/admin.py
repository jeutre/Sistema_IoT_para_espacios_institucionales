from django.contrib import admin
from .models import EventoOcupacion


@admin.register(EventoOcupacion)
class EventoOcupacionAdmin(admin.ModelAdmin):
    list_display  = ['dispositivo', 'estado', 'registrado_en']
    list_filter   = ['estado', 'dispositivo']
    search_fields = ['dispositivo__identificador']
