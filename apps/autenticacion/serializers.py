from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import SesionUsuario


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )


class MiTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Registra la sesion (HU-01) e incluye datos del usuario en el token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['nombre'] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get('request')
        ip = None
        if request is not None:
            reenviada = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = reenviada.split(',')[0].strip() if reenviada else request.META.get('REMOTE_ADDR')
        SesionUsuario.objects.create(usuario=self.user, ip=ip)
        data['usuario'] = UsuarioSerializer(self.user).data
        return data