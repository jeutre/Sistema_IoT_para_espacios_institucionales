from rest_framework import serializers
from .models import Laboratorio


class LaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Laboratorio
        fields = ['id', 'nombre', 'ubicacion', 'capacidad', 'activo', 'creado_en']
        read_only_fields = ['id', 'creado_en']

    def validate_capacidad(self, value):
        if value <= 0:
            raise serializers.ValidationError('La capacidad debe ser mayor a 0.')
        return value

    def validate_nombre(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return value.strip()