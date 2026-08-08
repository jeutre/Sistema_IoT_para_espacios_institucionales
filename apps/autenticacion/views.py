import logging
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SesionUsuario
from .serializers import UsuarioSerializer, SesionUsuarioSerializer

log = logging.getLogger(__name__)


def _client_ip(request) -> str:
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if not ip:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip.split(',')[0].strip() if ip else None


# ── Vistas clase (para urls.py) ─────────────────────────────────────────────

class LoginView(TokenObtainPairView):
    """HU-01 - Login que registra sesion en BD"""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(request, username=username, password=password)

            if user:
                ip = _client_ip(request)
                SesionUsuario.objects.create(
                    usuario=user,
                    token_refresh=response.data.get('refresh', ''),
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                )
                log.info(f"Login exitoso: {username} desde {ip}")

        return response


class LogoutView(generics.GenericAPIView):
    """HU-02 - Cerrar sesion"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            SesionUsuario.objects.filter(
                usuario=request.user,
                activa=True,
            ).update(
                activa=False,
                fecha_fin=timezone.now(),
            )

            log.info(f"Logout: {request.user.username}")
            return Response({'detail': 'Sesion cerrada exitosamente'})

        except Exception as e:
            log.error(f"Error en logout: {e}")
            return Response(
                {'detail': 'Error al cerrar sesion'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Vistas funcion (para urls_api.py) ───────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """HU-01 - Login via funcion"""
    jwt_view = LoginView.as_view()
    return jwt_view(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """HU-02 - Logout via funcion"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        SesionUsuario.objects.filter(
            usuario=request.user,
            activa=True,
        ).update(
            activa=False,
            fecha_fin=timezone.now(),
        )
        return Response({'detail': 'Sesion cerrada exitosamente'})
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def perfil_view(request):
    """Ver/editar perfil"""
    if request.method == 'GET':
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registro de nuevo usuario administrador."""
    serializer = UsuarioSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = User(**serializer.validated_data)
    user.set_password(request.data.get('password'))
    user.is_staff = True
    user.save()
    return Response(UsuarioSerializer(user).data, status=status.HTTP_201_CREATED)