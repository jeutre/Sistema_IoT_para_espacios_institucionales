from rest_framework import serializers
from .models import Equipo, EventoConexion
import re


class EquipoSerializer(serializers.ModelSerializer):
    minutos_inactivo = serializers.ReadOnlyField()

    class Meta:
        model  = Equipo
        fields = [
            'id', 'laboratorio', 'nombre', 'ip', 'mac', 'activo', 'creado_en',
            'estado_conexion', 'ultimo_ping', 'minutos_inactivo',
        ]
        read_only_fields = [
            'id', 'creado_en', 'estado_conexion', 'ultimo_ping', 'minutos_inactivo',
        ]

    def validate_mac(self, value):
        patron = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        if not re.match(patron, value):
            raise serializers.ValidationError('Formato MAC inválido. Use XX:XX:XX:XX:XX:XX')
        return value.upper()

    def validate_ip(self, value):
        if not value:
            raise serializers.ValidationError('La dirección IP es obligatoria.')
        return value


class EventoConexionSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)

    class Meta:
        model  = EventoConexion
        fields = ['id', 'equipo', 'equipo_nombre', 'tipo', 'registrado_en']
        read_only_fields = ['id', 'registrado_en']