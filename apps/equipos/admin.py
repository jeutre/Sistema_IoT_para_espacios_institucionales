from django.contrib import admin
from .models import Equipo


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'laboratorio', 'ip', 'mac', 'activo']
    list_filter   = ['activo', 'laboratorio']
    search_fields = ['nombre', 'ip', 'mac']
