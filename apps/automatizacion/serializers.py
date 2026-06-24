from rest_framework import serializers
from .models import ReglaAutomatizacion

class ReglaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaAutomatizacion
        fields = '__all__'
