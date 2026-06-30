from rest_framework import serializers
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.core.exceptions import ValidationError
from .models import Dispositivo, HistorialComunicacion


class DispositivoSerializer(serializers.ModelSerializer):
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    
    class Meta:
        model  = Dispositivo
        fields = ['id', 'laboratorio', 'laboratorio_nombre', 'identificador', 'ip', 'estado', 'ultima_conexion', 'creado_en']
        read_only_fields = ['id', 'estado', 'ultima_conexion', 'creado_en', 'laboratorio_nombre']

    def validate_ip(self, value):
        if not value:
            raise serializers.ValidationError('La dirección IP es obligatoria.')
        
        # Validar formato de IP
        try:
            # Intentar validar como IPv4
            validate_ipv4_address(value)
        except ValidationError:
            try:
                # Intentar validar como IPv6
                validate_ipv6_address(value)
            except ValidationError:
                raise serializers.ValidationError('La dirección IP no tiene un formato válido (IPv4 o IPv6).')
        
        return value

    def validate_identificador(self, value):
        if not value:
            raise serializers.ValidationError('El identificador del dispositivo es obligatorio.')
        
        # Validar longitud mínima
        if len(value) < 3:
            raise serializers.ValidationError('El identificador debe tener al menos 3 caracteres.')
        
        # Validar caracteres permitidos (letras, números, guiones, puntos)
        import re
        if not re.match(r'^[a-zA-Z0-9\-\._]+$', value):
            raise serializers.ValidationError('El identificador solo puede contener letras, números, guiones, puntos y guiones bajos.')
        
        return value

    def validate(self, data):
        # Validaciones cruzadas
        if 'ip' in data and 'identificador' in data:
            # Verificar que no exista otro dispositivo con la misma IP
            existing_ip = Dispositivo.objects.filter(ip=data['ip']).exclude(pk=self.instance.pk if self.instance else None)
            if existing_ip.exists():
                raise serializers.ValidationError({'ip': 'Ya existe un dispositivo con esta dirección IP.'})
            
            # Verificar que no exista otro dispositivo con el mismo identificador
            existing_id = Dispositivo.objects.filter(identificador=data['identificador']).exclude(pk=self.instance.pk if self.instance else None)
            if existing_id.exists():
                raise serializers.ValidationError({'identificador': 'Ya existe un dispositivo con este identificador.'})
        
        return data


class HistorialComunicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HistorialComunicacion
        fields = ['id', 'dispositivo', 'mensaje', 'recibido_en']
        read_only_fields = ['id', 'recibido_en']