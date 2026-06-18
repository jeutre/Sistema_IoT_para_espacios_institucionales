from rest_framework import serializers
from .models import Dispositivo, HistorialComunicacion


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Dispositivo
        fields = ['id', 'laboratorio', 'identificador', 'ip', 'estado', 'ultima_conexion', 'creado_en']
        read_only_fields = ['id', 'estado', 'ultima_conexion', 'creado_en']

    def validate_ip(self, value):
        if not value:
            raise serializers.ValidationError('La dirección IP es obligatoria.')
        return value


class HistorialComunicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HistorialComunicacion
        fields = ['id', 'dispositivo', 'mensaje', 'recibido_en']
        read_only_fields = ['id', 'recibido_en']