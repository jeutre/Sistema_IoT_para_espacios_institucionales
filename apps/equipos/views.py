import platform
import asyncio
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from asgiref.sync import sync_to_async

from .models import Equipo, EventoConexion
from .serializers import EquipoSerializer, EventoConexionSerializer


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
    Incluye timeout de seguridad para que nunca se quede colgado.
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


@sync_to_async
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
        estado      = self.request.query_params.get('estado')

        if laboratorio:
            queryset = queryset.filter(laboratorio__id=laboratorio)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        if estado in ('activo', 'inactivo'):
            queryset = queryset.filter(estado_conexion=estado)

        return queryset

    @action(detail=True, methods=['get'], url_path='ping')
    async def ping(self, request, pk=None):
        """
        Verifica conectividad de UN equipo. (HU-14)
        """
        equipo   = await sync_to_async(self.get_object)()
        responde = await ejecutar_ping(equipo.ip)
        cambio   = await actualizar_estado_equipo(equipo, responde)

        return Response({
            'equipo':           equipo.nombre,
            'ip':               equipo.ip,
            'responde':         responde,
            'estado_conexion':  equipo.estado_conexion,
            'cambio_de_estado': cambio,
            'timestamp':        equipo.ultimo_ping,
        })

    @action(detail=False, methods=['get'], url_path='ping-todos')
    async def ping_todos(self, request):
        """
        Verifica conectividad de TODOS los equipos concurrentemente. (HU-14)
        Los pings corren en paralelo — no en secuencia — así 30 equipos
        tardan lo mismo que 1 solo ping.
        """
        equipos = await sync_to_async(list)(Equipo.objects.filter(activo=True))

        async def procesar_equipo(equipo):
            responde = await ejecutar_ping(equipo.ip)
            cambio   = await actualizar_estado_equipo(equipo, responde)
            return {
                'equipo':           equipo.nombre,
                'ip':               equipo.ip,
                'estado_conexion':  equipo.estado_conexion,
                'cambio_de_estado': cambio,
            }

        tasks      = [procesar_equipo(e) for e in equipos]
        resultados = await asyncio.gather(*tasks)

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

        page = self.paginate_queryset(eventos)
        if page is not None:
            serializer = EventoConexionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EventoConexionSerializer(eventos, many=True)
        return Response(serializer.data)


class EventoConexionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listado general de TODOS los eventos de conexión/desconexión. (HU-17)
    Solo lectura: estos eventos los crea el sistema automáticamente.
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