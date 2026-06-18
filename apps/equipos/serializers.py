from rest_framework import serializers
from .models import Equipo
import re


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Equipo
        fields = ['id', 'laboratorio', 'nombre', 'ip', 'mac', 'activo', 'creado_en']
        read_only_fields = ['id', 'creado_en']

    def validate_mac(self, value):
        patron = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        if not re.match(patron, value):
            raise serializers.ValidationError('Formato MAC inválido. Use XX:XX:XX:XX:XX:XX')
        return value.upper()

    def validate_ip(self, value):
        if not value:
            raise serializers.ValidationError('La dirección IP es obligatoria.')
        return value