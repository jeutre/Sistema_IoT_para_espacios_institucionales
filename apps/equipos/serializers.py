from rest_framework import serializers
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Equipo, EventoConexion
import re


class EquipoSerializer(serializers.ModelSerializer):
    minutos_inactivo = serializers.ReadOnlyField()

    class Meta:
        model = Equipo
        fields = [
            'id', 'laboratorio', 'nombre', 'ip', 'mac', 'activo', 'creado_en',
            'estado_conexion', 'ultimo_ping', 'minutos_inactivo',
            'tiene_relay', 'relay_gpio', 'consumo_watts', 'posicion_fisica',
        ]
        read_only_fields = [
            'id', 'creado_en', 'estado_conexion', 'ultimo_ping', 'minutos_inactivo',
        ]

    def validate_mac(self, value):
        patron = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        if not re.match(patron, value):
            raise serializers.ValidationError('Formato MAC invalido. Use XX:XX:XX:XX:XX:XX')
        return value.upper()

    def validate_ip(self, value):
        if not value:
            raise serializers.ValidationError('La direccion IP es obligatoria.')
        try:
            validate_ipv4_address(value)
        except DjangoValidationError:
            raise serializers.ValidationError('La IP debe ser IPv4 valida (ej: 192.168.1.10).')
        return value


class EventoConexionSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)

    class Meta:
        model = EventoConexion
        fields = ['id', 'equipo', 'equipo_nombre', 'tipo', 'registrado_en']
        read_only_fields = ['id', 'registrado_en']