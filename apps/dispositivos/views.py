import platform
import asyncio
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from asgiref.sync import sync_to_async

from .models import Dispositivo, HistorialComunicacion
from .serializers import DispositivoSerializer, HistorialComunicacionSerializer


def _ping_args(ip: str) -> list:
    """
    Devuelve los argumentos correctos del comando ping según el SO.
    Windows : ping -n 1 -w 1000 <ip>   (timeout en milisegundos)
    Linux/Mac: ping -c 1 -W 1    <ip>   (timeout en segundos)
    """
    if platform.system().lower() == 'windows':
        return ['ping', '-n', '1', '-w', '1000', ip]
    return ['ping', '-c', '1', '-W', '1', ip]


async def ejecutar_ping(ip: str) -> bool:
    """
    Ejecuta un ping real y devuelve True si el host responde.
    Captura cualquier excepción para que nunca rompa la vista.
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *_ping_args(ip),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(process.communicate(), timeout=3)
        return process.returncode == 0
    except asyncio.TimeoutError:
        try:
            process.kill()
        except Exception:
            pass
        return False
    except Exception:
        return False


class DispositivoViewSet(viewsets.ModelViewSet):
    serializer_class   = DispositivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dispositivo.objects.all()

    @action(detail=True, methods=['get'], url_path='ping')
    async def ping(self, request, pk=None):
        """
        Verifica si el ESP32 responde (HU-07).
        Funciona en Windows y Linux/Mac.
        """
        dispositivo = await sync_to_async(self.get_object)()

        conectado = await ejecutar_ping(dispositivo.ip)

        dispositivo.estado          = 'conectado' if conectado else 'desconectado'
        dispositivo.ultima_conexion = timezone.now()
        await sync_to_async(dispositivo.save)()

        return Response({
            'dispositivo': dispositivo.identificador,
            'ip':          dispositivo.ip,
            'estado':      dispositivo.estado,
            'timestamp':   dispositivo.ultima_conexion,
        })


class HistorialComunicacionViewSet(viewsets.ModelViewSet):
    serializer_class   = HistorialComunicacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset     = HistorialComunicacion.objects.all()
        dispositivo  = self.request.query_params.get('dispositivo')
        if dispositivo:
            queryset = queryset.filter(dispositivo__id=dispositivo)
        return queryset

    @action(detail=False, methods=['post'], url_path='recibir', permission_classes=[HasAPIKey])
    def recibir(self, request):
        """
        Endpoint que recibe mensajes del ESP32 (protegido con API Key).
        """
        dispositivo_id = request.data.get('dispositivo_id')
        mensaje        = request.data.get('mensaje')

        if not dispositivo_id or not mensaje:
            return Response(
                {'error': 'dispositivo_id y mensaje son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            dispositivo = Dispositivo.objects.get(id=dispositivo_id)
        except Dispositivo.DoesNotExist:
            return Response({'error': 'Dispositivo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        dispositivo.ultima_conexion = timezone.now()
        dispositivo.estado          = 'conectado'
        dispositivo.save()

        historial = HistorialComunicacion.objects.create(
            dispositivo=dispositivo,
            mensaje=mensaje
        )

        return Response(
            HistorialComunicacionSerializer(historial).data,
            status=status.HTTP_201_CREATED
        )