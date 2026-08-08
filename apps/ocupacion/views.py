import logging
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.utils import timezone
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action, api_view, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

from apps.dispositivos.models import Dispositivo, HistorialComunicacion
from .models import EventoOcupacion
from .serializers import (
    EventoOcupacionSerializer,
    EventoOcupacionCreateSerializer,
    OcupacionTiempoRealSerializer,
)

log = logging.getLogger(__name__)


class ESP32PIRThrottle(UserRateThrottle):
    """Rate limit especifico para datos PIR del ESP32 (HU-09)."""
    scope = 'esp32_pir'
    rate = '10/minute'


class EventoOcupacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    HU-11 - Historial de ocupacion (listado con filtros).
    Filtros soportados:
      ?dispositivo=<id>      - filtra por dispositivo ESP32
      ?estado=ocupado|vacio  - filtra por estado
      ?desde=YYYY-MM-DD      - filtra por fecha minima (inclusive)
      ?hasta=YYYY-MM-DD      - filtra por fecha maxima (inclusive)
    """
    queryset = EventoOcupacion.objects.select_related(
        'dispositivo', 'dispositivo__laboratorio'
    ).all()
    serializer_class = EventoOcupacionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['dispositivo', 'estado']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        qs = super().get_queryset()
        desde = self.request.query_params.get('desde')
        hasta = self.request.query_params.get('hasta')
        if desde:
            qs = qs.filter(timestamp__date__gte=desde)
        if hasta:
            qs = qs.filter(timestamp__date__lte=hasta)
        return qs


class RecibirPIRView(generics.CreateAPIView):
    """
    HU-09 - Endpoint POST donde el ESP32 envia datos del sensor PIR.
    Protegido por API Key (no por JWT de usuario).
    """
    serializer_class = EventoOcupacionCreateSerializer
    permission_classes = [HasAPIKey]
    throttle_classes = [ESP32PIRThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dispositivo_id = serializer.validated_data['dispositivo_id']
        estado_pir = serializer.validated_data['estado']

        try:
            dispositivo = Dispositivo.objects.select_related('laboratorio').get(
                id=dispositivo_id
            )
        except Dispositivo.DoesNotExist:
            return Response(
                {'error': f'Dispositivo id={dispositivo_id} no encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )

        evento = EventoOcupacion.objects.create(
            dispositivo=dispositivo,
            estado=estado_pir,
        )

        dispositivo.estado = 'conectado'
        dispositivo.ultima_conexion = timezone.now()
        dispositivo.save(update_fields=['estado', 'ultima_conexion', 'actualizado_en'])

        HistorialComunicacion.objects.create(
            dispositivo=dispositivo,
            tipo_evento='pir_dato',
            datos={'estado_pir': estado_pir},
            exitoso=True,
        )

        log.info(
            f"PIR -> {dispositivo.identificador}: {estado_pir} "
            f"(Lab: {dispositivo.laboratorio.nombre})"
        )

        output = EventoOcupacionSerializer(evento)
        return Response(output.data, status=status.HTTP_201_CREATED)


class OcupacionTiempoRealView(generics.GenericAPIView):
    """
    HU-10 - Ocupacion en tiempo real.
    Devuelve el ultimo estado reportado por cada dispositivo PIR.
    """
    serializer_class = OcupacionTiempoRealSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        dispositivos = Dispositivo.objects.filter(tipo='esp32').select_related('laboratorio')
        resultado = []

        for disp in dispositivos:
            ultimo = EventoOcupacion.objects.filter(
                dispositivo=disp
            ).order_by('-timestamp').first()

            if ultimo:
                segundos = (timezone.now() - ultimo.timestamp).total_seconds()
                resultado.append({
                    'dispositivo': disp.identificador,
                    'laboratorio': disp.laboratorio.nombre,
                    'estado': ultimo.estado,
                    'ultimo_evento': ultimo.timestamp,
                    'segundos_ultimo_evento': round(segundos, 1),
                })
            else:
                resultado.append({
                    'dispositivo': disp.identificador,
                    'laboratorio': disp.laboratorio.nombre,
                    'estado': 'sin_datos',
                    'ultimo_evento': None,
                    'segundos_ultimo_evento': None,
                })

        return Response(resultado)


class HorasPicoView(generics.GenericAPIView):
    """
    HU-12 - Horas pico de ocupacion.
    GET /api/v1/ocupacion/horas-pico/
    GET /api/v1/ocupacion/horas-pico/?desde=2026-06-01&hasta=2026-06-30

    Cuenta, por cada hora del dia (0-23), cuantos eventos 'ocupado' hubo.
    Devuelve la hora pico y el detalle completo por hora.
    """
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')

        qs = EventoOcupacion.objects.all()
        if desde:
            qs = qs.filter(timestamp__date__gte=desde)
        if hasta:
            qs = qs.filter(timestamp__date__lte=hasta)

        qs_ocupado = qs.filter(estado='ocupado')
        por_hora = (
            qs_ocupado
            .annotate(hora=ExtractHour('timestamp'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('hora')
        )
        detalle = [
            {'hora': int(item['hora']), 'total_eventos_ocupado': int(item['total'])}
            for item in por_hora
        ]

        hora_pico = None
        if detalle:
            max_total = max(d['total_eventos_ocupado'] for d in detalle)
            if max_total > 0:
                hora_pico = next(d for d in detalle if d['total_eventos_ocupado'] == max_total)

        return Response({
            'hora_pico': hora_pico,
            'detalle_por_hora': detalle,
        })