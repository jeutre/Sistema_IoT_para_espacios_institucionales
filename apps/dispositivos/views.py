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
from .utils import log_device_ping, log_device_connection_change


def _ping_args(ip: str) -> list:
    """
    Devuelve los argumentos correctos del comando ping según el SO.
    Windows : ping -n 1 -w 1000 <ip>   (timeout en milisegundos)
    Linux/Mac: ping -c 1 -W 1    <ip>   (timeout en segundos)
    """
    if platform.system().lower() == 'windows':
        return ['ping', '-n', '1', '-w', '1000', ip]
    return ['ping', '-c', '1', '-W', '1', ip]


async def ejecutar_ping(ip: str) -> tuple:
    """
    Ejecuta un ping real y devuelve (conectado: bool, error_detail: str | None).
    Captura cualquier excepción para que nunca rompa la vista.
    """
    conectado = False
    error_detail = None
    try:
        process = await asyncio.create_subprocess_exec(
            *_ping_args(ip),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=3)
        conectado = process.returncode == 0
        if stderr:
            error_detail = stderr.decode('utf-8', errors='ignore')
    except FileNotFoundError:
        error_detail = 'Comando ping no encontrado en el sistema'
    except PermissionError:
        error_detail = 'Permiso denegado para ejecutar ping'
    except asyncio.TimeoutError:
        try:
            process.kill()
        except Exception:
            pass
        error_detail = 'Timeout al ejecutar ping'
    except Exception as e:
        error_detail = f'Error inesperado: {str(e)}'
    return conectado, error_detail


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
        try:
            dispositivo = await sync_to_async(self.get_object)()

            # Validar que la IP sea válida antes de hacer ping
            if not dispositivo.ip:
                return Response({
                    'error': 'El dispositivo no tiene una IP configurada',
                    'dispositivo': dispositivo.identificador,
                    'estado': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)

            conectado, error_detail = await ejecutar_ping(dispositivo.ip)

            old_status = dispositivo.estado
            dispositivo.estado          = 'conectado' if conectado else 'desconectado'
            dispositivo.ultima_conexion = timezone.now()
            await sync_to_async(dispositivo.save)()

            # Loggear el evento de ping
            log_device_ping(
                device_id=dispositivo.identificador,
                ip=dispositivo.ip,
                status='conectado' if conectado else 'desconectado',
                error=error_detail if not conectado else None
            )

            # Loggear cambio de estado si hubo
            if old_status != dispositivo.estado:
                log_device_connection_change(
                    device_id=dispositivo.identificador,
                    old_status=old_status,
                    new_status=dispositivo.estado
                )

            response_data = {
                'dispositivo': dispositivo.identificador,
                'ip':          dispositivo.ip,
                'estado':      dispositivo.estado,
                'timestamp':   dispositivo.ultima_conexion,
                'conectado':   conectado,
            }

            if error_detail and not conectado:
                response_data['error_detail'] = error_detail

            return Response(response_data)

        except Exception as e:
            return Response({
                'error': 'Error interno al procesar la solicitud de ping',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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