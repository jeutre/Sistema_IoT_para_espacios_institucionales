import subprocess
import logging
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Equipo, EventoConexion
from .serializers import EquipoSerializer, EventoConexionSerializer

log = logging.getLogger(__name__)


def ejecutar_ping(ip):
    """
    Ejecuta un ping ICMP a la IP dada usando el comando 'ping' de Linux
    (el contenedor corre sobre python:3.12-slim / debian, no Windows).
    Devuelve True si el host responde, False en caso contrario.
    """
    timeout = settings.IOT_CONFIG['PING_TIMEOUT_SEGUNDOS']
    try:
        resultado = subprocess.run(
            ['ping', '-c', '1', '-W', str(timeout), str(ip)],
            capture_output=True,
            timeout=timeout + 2,
        )
        return resultado.returncode == 0
    except Exception:
        return False


def actualizar_estado_equipo(equipo, responde):
    """
    Actualiza estado_conexion/ultima_actividad de un Equipo según el
    resultado del ping, y registra un EventoConexion si el estado cambió.
    Devuelve True si hubo cambio de estado, False si no.
    """
    estado_anterior = equipo.estado_conexion
    if responde:
        equipo.estado_conexion = 'activo'
        equipo.ultima_actividad = timezone.now()
    else:
        equipo.estado_conexion = 'inactivo'
    equipo.save(update_fields=['estado_conexion', 'ultima_actividad', 'actualizado_en'])

    hubo_cambio = estado_anterior != equipo.estado_conexion
    if hubo_cambio:
        EventoConexion.objects.create(
            equipo=equipo,
            tipo_evento='conexion' if responde else 'desconexion',
            estado_anterior=estado_anterior,
            estado_nuevo=equipo.estado_conexion,
        )
    return hubo_cambio


class EquipoViewSet(viewsets.ModelViewSet):
    """
    HU-13: Registrar IPv4
    HU-13B: Registrar MAC
    """
    queryset = Equipo.objects.select_related('laboratorio').all()
    serializer_class = EquipoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['laboratorio', 'estado_conexion', 'tiene_relay']
    search_fields = ['nombre', 'ip', 'mac']
    ordering_fields = ['nombre', 'ip']

    @action(detail=True, methods=['get'], url_path='ping')
    def ping(self, request, pk=None):
        """Ping a un equipo específico"""
        equipo = self.get_object()
        responde = ejecutar_ping(equipo.ip)
        actualizar_estado_equipo(equipo, responde)

        return Response({
            'equipo': equipo.id,
            'nombre': equipo.nombre,
            'ip': str(equipo.ip),
            'responde': responde,
            'estado_conexion': equipo.estado_conexion,
        })

    @action(detail=False, methods=['post'], url_path='ping-todos')
    def ping_todos(self, request):
        """Ping a todos los equipos del laboratorio"""
        resultados = []

        for equipo in self.get_queryset():
            responde = ejecutar_ping(equipo.ip)
            actualizar_estado_equipo(equipo, responde)

            resultados.append({
                'equipo': equipo.id,
                'nombre': equipo.nombre,
                'ip': str(equipo.ip),
                'responde': responde,
                'estado_conexion': equipo.estado_conexion,
            })

        return Response({'resultados': resultados, 'total': len(resultados)})


class EventoConexionViewSet(viewsets.ModelViewSet):
    """
    HU-17: Consultar historial de eventos de conexión
    """
    serializer_class = EventoConexionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EventoConexion.objects.select_related('equipo').all()
        equipo = self.request.query_params.get('equipo')
        tipo = self.request.query_params.get('tipo')

        if equipo:
            queryset = queryset.filter(equipo__id=equipo)
        # Aceptar todos los tipos válidos definidos en el modelo (HU-17):
        # conexion, desconexion, suspension, apagado, encendido
        tipos_validos = [t for t, _ in EventoConexion.TIPO_CHOICES]
        if tipo and tipo in tipos_validos:
            queryset = queryset.filter(tipo=tipo)

        return queryset