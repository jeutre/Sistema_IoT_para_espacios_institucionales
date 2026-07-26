from rest_framework import serializers
from django.utils import timezone
from .models import Alerta

class AlertaSerializer(serializers.ModelSerializer):
    dispositivo_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_relativo = serializers.SerializerMethodField()

    class Meta:
        model = Alerta
        fields = '__all__'
        read_only_fields = ['creado_en']

    def get_dispositivo_nombre(self, obj):
        if obj.objeto_relacionado:
            return getattr(obj.objeto_relacionado, 'nombre', getattr(obj.objeto_relacionado, 'identificador', 'Desconocido'))
        return "Sistema"
        
    def get_tiempo_relativo(self, obj):
        now = timezone.now()
        diff = now - obj.creado_en
        if diff.days > 0:
            return f"Hace {diff.days} d"
        elif diff.seconds >= 3600:
            horas = diff.seconds // 3600
            return f"Hace {horas} h"
        elif diff.seconds >= 60:
            minutos = diff.seconds // 60
            return f"Hace {minutos} min"
        else:
            return "Ahora"
