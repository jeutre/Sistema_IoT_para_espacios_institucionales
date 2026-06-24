from rest_framework import serializers
from .models import Comando

class ComandoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comando
        fields = '__all__'
        read_only_fields = ['estado', 'creado_en', 'ejecutado_en']
