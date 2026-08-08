from rest_framework import serializers
from .models import Dispositivo, HistorialComunicacion


class DispositivoSerializer(serializers.ModelSerializer):
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    esta_conectado = serializers.ReadOnlyField()

    class Meta:
        model = Dispositivo
        fields = [
            'id', 'identificador', 'tipo', 'laboratorio', 'laboratorio_nombre',
            'mac_address', 'ip', 'api_key', 'estado', 'esta_conectado',
            'ultima_conexion', 'firmware_version', 'creado_en', 'actualizado_en',
        ]
        read_only_fields = ['id', 'estado', 'ultima_conexion', 'creado_en', 'actualizado_en']
        extra_kwargs = {'api_key': {'write_only': True}}


class DispositivoReadSerializer(serializers.ModelSerializer):
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    esta_conectado = serializers.ReadOnlyField()

    class Meta:
        model = Dispositivo
        fields = [
            'id', 'identificador', 'tipo', 'laboratorio', 'laboratorio_nombre',
            'mac_address', 'ip', 'estado', 'esta_conectado',
            'ultima_conexion', 'firmware_version', 'creado_en', 'actualizado_en',
        ]


class HistorialComunicacionSerializer(serializers.ModelSerializer):
    dispositivo_identificador = serializers.CharField(source='dispositivo.identificador', read_only=True)

    class Meta:
        model = HistorialComunicacion
        fields = [
            'id', 'dispositivo', 'dispositivo_identificador',
            'tipo_evento', 'mensaje', 'datos', 'exitoso', 'recibido_en',
        ]
        read_only_fields = ['id', 'recibido_en']


class PingResultSerializer(serializers.Serializer):
    dispositivo = serializers.CharField()
    ip = serializers.CharField()
    estado = serializers.CharField()
    timestamp = serializers.DateTimeField(allow_null=True)
    conectado = serializers.BooleanField()