from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import subprocess

from .models import Dispositivo, HistorialComunicacion
from .serializers import DispositivoSerializer, HistorialComunicacionSerializer


class DispositivoViewSet(viewsets.ModelViewSet):
    serializer_class   = DispositivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dispositivo.objects.all()

    @action(detail=True, methods=['get'], url_path='ping')
    def ping(self, request, pk=None):
        """
        Verifica si el ESP32 responde (HU-07)
        """
        dispositivo = self.get_object()
        try:
            resultado = subprocess.run(
                ['ping', '-n', '1', '-w', '1000', dispositivo.ip],
                capture_output=True
            )
            conectado = resultado.returncode == 0
        except Exception:
            conectado = False

        dispositivo.estado          = 'conectado' if conectado else 'desconectado'
        dispositivo.ultima_conexion = timezone.now()
        dispositivo.save()

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

    @action(detail=False, methods=['post'], url_path='recibir', permission_classes=[AllowAny])
    def recibir(self, request):
        """
        Endpoint que recibe mensajes del ESP32 (HU-08)
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