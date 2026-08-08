from django.contrib import admin
from .models import Laboratorio


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'capacidad', 'estado', 'actualizado_en']
    list_filter = ['estado']
    search_fields = ['nombre', 'ubicacion']