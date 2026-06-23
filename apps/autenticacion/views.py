from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import SesionUsuario
from .serializers import LoginSerializer, UsuarioSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    usuario = authenticate(request, username=username, password=password)

    if usuario is None:
        return Response(
            {'error': 'Credenciales incorrectas.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, usuario)

    ip = request.META.get('REMOTE_ADDR')
    SesionUsuario.objects.create(usuario=usuario, ip=ip)

    return Response({
        'mensaje': f'Bienvenido {usuario.username}',
        'usuario': UsuarioSerializer(usuario).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    SesionUsuario.objects.filter(
        usuario=request.user, activa=True
    ).update(activa=False)

    logout(request)
    return Response({'mensaje': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_view(request):
    return Response(UsuarioSerializer(request.user).data)

