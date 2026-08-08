from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import SesionUsuario


class MiTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT con datos extra del usuario (rol único: administrador)."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # El backlog define un único rol (administrador institucional);
        # exponemos is_staff para que el frontend pueda validarlo.
        token['is_staff'] = user.is_staff
        token['username'] = user.username
        return token


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el usuario administrador (django.contrib.auth.User)."""

    ultimo_login_ip = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'last_login', 'ultimo_login_ip']
        read_only_fields = ['id', 'ultimo_login_ip', 'is_staff', 'last_login']

    def get_ultimo_login_ip(self, obj):
        ultima = (SesionUsuario.objects.filter(usuario=obj)
                  .order_by('-inicio').first())
        return ultima.ip if ultima else None


class SesionUsuarioSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = SesionUsuario
        fields = [
            'id', 'usuario', 'usuario_username',
            'ip', 'inicio', 'fecha_fin',
            'activa', 'user_agent',
        ]
        read_only_fields = ['id', 'inicio']


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()