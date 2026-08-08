from django.contrib import admin
from .models import EventoOcupacion


@admin.register(EventoOcupacion)
class EventoOcupacionAdmin(admin.ModelAdmin):
    list_display = ['dispositivo', 'estado', 'timestamp']
    list_filter = ['estado', 'dispositivo']
    date_hierarchy = 'timestamp'