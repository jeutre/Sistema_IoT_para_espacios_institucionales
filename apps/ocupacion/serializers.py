from rest_framework import serializers
from .models import EventoOcupacion


class EventoOcupacionSerializer(serializers.ModelSerializer):
    """Serializer de lectura para el historial de ocupación (HU-11)."""

    class Meta:
        model  = EventoOcupacion
        fields = ['id', 'dispositivo', 'estado', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class EventoOcupacionCreateSerializer(serializers.Serializer):
    """
    HU-09 — Payload que envía el firmware del ESP32 al endpoint /ocupacion/pir/.

    El ESP32 envía exactamente este JSON:
        { "dispositivo_id": 1, "estado": "ocupado" | "vacio" }
    """
    dispositivo_id = serializers.IntegerField(min_value=1)
    estado = serializers.ChoiceField(choices=['ocupado', 'vacio'])

    def validate_dispositivo_id(self, value):
        from apps.dispositivos.models import Dispositivo
        if not Dispositivo.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'No existe un dispositivo con id={value}.'
            )
        return value


class OcupacionTiempoRealSerializer(serializers.Serializer):
    """
    HU-10 — Respuesta del endpoint /ocupacion/tiempo-real/.
    Devuelve el último estado reportado por cada dispositivo PIR.
    """
    dispositivo              = serializers.CharField()
    laboratorio              = serializers.CharField()
    estado                   = serializers.CharField()
    ultimo_evento            = serializers.DateTimeField(allow_null=True)
    segundos_ultimo_evento   = serializers.FloatField(allow_null=True)