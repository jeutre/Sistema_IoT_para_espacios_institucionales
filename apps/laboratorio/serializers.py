from rest_framework import serializers
from .models import Laboratorio


class LaboratorioSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )

    class Meta:
        model = Laboratorio
        fields = [
            'id', 'nombre', 'ubicacion', 'capacidad', 'estado',
            'estado_display', 'horario_apertura', 'horario_cierre',
            'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']