from rest_framework import serializers
from .models import EventoOcupacion


class EventoOcupacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EventoOcupacion
        fields = ['id', 'dispositivo', 'estado', 'registrado_en']
        read_only_fields = ['id', 'registrado_en']

    def validate_estado(self, value):
        if value not in ['ocupado', 'vacio']:
            raise serializers.ValidationError('Estado debe ser ocupado o vacio.')
        return value