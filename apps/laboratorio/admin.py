from django.contrib import admin
from .models import Laboratorio
 

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'ubicacion', 'capacidad', 'activo', 'creado_en']
    list_filter   = ['activo']
    search_fields = ['nombre', 'ubicacion']
    ordering      = ['nombre']
    