from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import subprocess

from .models import Equipo, EventoConexion
from .serializers import EquipoSerializer, EventoConexionSerializer


def verificar_ping(ip):
    """
    Ejecuta un ping real al equipo y devuelve True/False.
    Funciona en Windows (-n) y Linux/Mac (-c).
    """
    import platform
    parametro_cantidad = '-n' if platform.system().lower() == 'windows' else '-c'
    try:
        resultado = subprocess.run(
            ['ping', parametro_cantidad, '1', '-w', '1000', ip] if platform.system().lower() == 'windows'
            else ['ping', parametro_cantidad, '1', '-W', '1', ip],
            capture_output=True
        )
        return resultado.returncode == 0
    except Exception:
        return False


def actualizar_estado_equipo(equipo, responde):
    """
    Actualiza el estado de un equipo y, SOLO SI CAMBIÓ,
    registra un EventoConexion. (HU-17)
    """
    estado_anterior = equipo.estado_conexion
    estado_nuevo    = 'activo' if responde else 'inactivo'

    equipo.estado_conexion = estado_nuevo
    equipo.ultimo_ping     = timezone.now()
    equipo.save()

    hubo_cambio = estado_anterior != estado_nuevo

    if hubo_cambio:
        EventoConexion.objects.create(
            equipo=equipo,
            tipo='conexion' if estado_nuevo == 'activo' else 'desconexion'
        )

    return hubo_cambio


class EquipoViewSet(viewsets.ModelViewSet):
    serializer_class   = EquipoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset    = Equipo.objects.all()
        laboratorio = self.request.query_params.get('laboratorio')
        activo      = self.request.query_params.get('activo')
        estado      = self.request.query_params.get('estado')  # HU-15 / HU-16

        if laboratorio:
            queryset = queryset.filter(laboratorio__id=laboratorio)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        if estado in ('activo', 'inactivo'):
            queryset = queryset.filter(estado_conexion=estado)

        return queryset

    @action(detail=True, methods=['get'], url_path='ping')
    def ping(self, request, pk=None):
        """
        Verifica conectividad de UN equipo. (HU-14)
        GET /api/v1/equipos/<id>/ping/
        """
        equipo   = self.get_object()
        responde = verificar_ping(equipo.ip)
        cambio   = actualizar_estado_equipo(equipo, responde)

        return Response({
            'equipo':           equipo.nombre,
            'ip':               equipo.ip,
            'responde':         responde,
            'estado_conexion':  equipo.estado_conexion,
            'cambio_de_estado': cambio,
            'timestamp':        equipo.ultimo_ping,
        })

    @action(detail=False, methods=['get'], url_path='ping-todos')
    def ping_todos(self, request):
        """
        Verifica conectividad de TODOS los equipos. (HU-14)
        GET /api/v1/equipos/ping-todos/
        """
        equipos    = Equipo.objects.filter(activo=True)
        resultados = []

        for equipo in equipos:
            responde = verificar_ping(equipo.ip)
            cambio   = actualizar_estado_equipo(equipo, responde)

            resultados.append({
                'equipo':           equipo.nombre,
                'ip':               equipo.ip,
                'estado_conexion':  equipo.estado_conexion,
                'cambio_de_estado': cambio,
            })

        total_activos = sum(1 for r in resultados if r['estado_conexion'] == 'activo')

        return Response({
            'total_equipos':   len(resultados),
            'total_activos':   total_activos,
            'total_inactivos': len(resultados) - total_activos,
            'detalle':         resultados,
        })

    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None):
        """
        Historial de actividad de UN equipo, con filtro de fechas. (HU-18)
        GET /api/v1/equipos/<id>/historial/
        GET /api/v1/equipos/<id>/historial/?desde=2026-06-01&hasta=2026-06-20
        """
        equipo  = self.get_object()
        eventos = EventoConexion.objects.filter(equipo=equipo)

        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')

        if desde:
            eventos = eventos.filter(registrado_en__date__gte=desde)
        if hasta:
            eventos = eventos.filter(registrado_en__date__lte=hasta)

        serializer = EventoConexionSerializer(eventos, many=True)
        return Response(serializer.data)


class EventoConexionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listado general de TODOS los eventos de conexión/desconexión. (HU-17)
    Solo lectura: estos eventos los crea el sistema automáticamente, nadie los edita a mano.
    """
    serializer_class   = EventoConexionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = EventoConexion.objects.all()
        equipo   = self.request.query_params.get('equipo')
        tipo     = self.request.query_params.get('tipo')

        if equipo:
            queryset = queryset.filter(equipo__id=equipo)
        if tipo in ('conexion', 'desconexion'):
            queryset = queryset.filter(tipo=tipo)

        return queryset