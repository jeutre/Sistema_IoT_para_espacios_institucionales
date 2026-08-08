import platform
import subprocess
import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from .models import Dispositivo, HistorialComunicacion
from .serializers import (
    DispositivoSerializer, DispositivoReadSerializer,
    HistorialComunicacionSerializer, PingResultSerializer,
)

log = logging.getLogger(__name__)


def _ping_args(ip):
    if platform.system().lower() == 'windows':
        return ['ping', '-n', '1', '-w', '3000', ip]
    return ['ping', '-c', '1', '-W', '3', ip]


def ejecutar_ping(ip):
    """Ejecuta ping real. Retorna (conectado: bool, error_detail: str|None)"""
    try:
        resultado = subprocess.run(
            _ping_args(ip),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return resultado.returncode == 0, None
    except subprocess.TimeoutExpired:
        return False, 'Timeout'
    except Exception as e:
        return False, str(e)


class DispositivoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return DispositivoReadSerializer
        return DispositivoSerializer

    def get_queryset(self):
        return Dispositivo.objects.select_related('laboratorio').all()

    @action(detail=True, methods=['get'], url_path='ping')
    def ping(self, request, pk=None):
        """HU-07 - Ping real al ESP32"""
        try:
            dispositivo = self.get_object()

            if not dispositivo.ip:
                return Response({
                    'error': 'El dispositivo no tiene IP configurada',
                    'dispositivo': dispositivo.identificador,
                    'estado': 'error',
                }, status=status.HTTP_400_BAD_REQUEST)

            conectado, error_detail = ejecutar_ping(dispositivo.ip)

            old_status = dispositivo.estado
            dispositivo.estado = 'conectado' if conectado else 'desconectado'
            dispositivo.ultima_conexion = timezone.now()
            dispositivo.save(update_fields=['estado', 'ultima_conexion', 'actualizado_en'])

            # Registrar en historial
            HistorialComunicacion.objects.create(
                dispositivo=dispositivo,
                tipo_evento='heartbeat',
                datos={'conectado': conectado, 'ip': str(dispositivo.ip)},
                exitoso=conectado,
            )

            if old_status != dispositivo.estado:
                log.info(f"ESP32 {dispositivo.identificador}: {old_status} -> {dispositivo.estado}")

            response_data = {
                'dispositivo': dispositivo.identificador,
                'ip': str(dispositivo.ip),
                'estado': dispositivo.estado,
                'timestamp': dispositivo.ultima_conexion,
                'conectado': conectado,
            }
            if error_detail and not conectado:
                response_data['error_detail'] = error_detail

            return Response(response_data)

        except Exception as e:
            log.error(f"Error en ping: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HistorialComunicacionViewSet(viewsets.ModelViewSet):
    serializer_class = HistorialComunicacionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = HistorialComunicacion.objects.select_related('dispositivo').all()
        dispositivo = self.request.query_params.get('dispositivo')
        if dispositivo:
            queryset = queryset.filter(dispositivo__id=dispositivo)
        return queryset

    @action(detail=False, methods=['post'], url_path='recibir', permission_classes=[HasAPIKey])
    def recibir(self, request):
        """Endpoint que recibe mensajes del ESP32 (API Key)"""
        dispositivo_id = request.data.get('dispositivo_id')
        mensaje = request.data.get('mensaje', '')

        if not dispositivo_id:
            return Response(
                {'error': 'dispositivo_id es obligatorio.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dispositivo = Dispositivo.objects.get(id=dispositivo_id)
        except Dispositivo.DoesNotExist:
            return Response({'error': 'Dispositivo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        dispositivo.ultima_conexion = timezone.now()
        dispositivo.estado = 'conectado'
        dispositivo.save(update_fields=['estado', 'ultima_conexion', 'actualizado_en'])

        historial = HistorialComunicacion.objects.create(
            dispositivo=dispositivo,
            tipo_evento='heartbeat',
            mensaje=mensaje,
            datos=request.data,
            exitoso=True,
        )

        return Response(
            HistorialComunicacionSerializer(historial).data,
            status=status.HTTP_201_CREATED,
        )