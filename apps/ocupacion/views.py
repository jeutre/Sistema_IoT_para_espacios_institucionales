from django.db.models import Count
from django.db.models.functions import ExtractHour
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import EventoOcupacion
from .serializers import EventoOcupacionSerializer
from apps.dispositivos.models import Dispositivo


class OcupacionViewSet(viewsets.ModelViewSet):
    serializer_class   = EventoOcupacionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names  = ['get', 'head', 'options']

    def get_queryset(self):
        """
        Listado general de eventos de ocupación, con filtros. (HU-11)
        ?dispositivo=<id>
        ?desde=2026-06-01&hasta=2026-06-20
        """
        queryset    = EventoOcupacion.objects.all()
        dispositivo = self.request.query_params.get('dispositivo')
        desde       = self.request.query_params.get('desde')
        hasta       = self.request.query_params.get('hasta')

        if dispositivo:
            queryset = queryset.filter(dispositivo__id=dispositivo)
        if desde:
            queryset = queryset.filter(registrado_en__date__gte=desde)
        if hasta:
            queryset = queryset.filter(registrado_en__date__lte=hasta)

        return queryset

    @action(detail=False, methods=['get'], url_path='tiempo-real')
    def tiempo_real(self, request):
        """
        Devuelve el estado actual de ocupación por dispositivo (HU-10)
        """
        dispositivos = Dispositivo.objects.all()
        resultado    = []

        for dispositivo in dispositivos:
            ultimo = EventoOcupacion.objects.filter(
                dispositivo=dispositivo
            ).first()

            resultado.append({
                'dispositivo':  dispositivo.identificador,
                'laboratorio':  dispositivo.laboratorio.nombre,
                'estado':       ultimo.estado if ultimo else 'sin datos',
                'ultima_vez':   ultimo.registrado_en if ultimo else None,
            })

        return Response(resultado)

    @action(detail=False, methods=['post'], url_path='pir', permission_classes=[AllowAny])
    def recibir_pir(self, request):
        """
        Endpoint que recibe datos del sensor PIR desde el ESP32 (HU-09)
        """
        dispositivo_id = request.data.get('dispositivo_id')
        estado         = request.data.get('estado')

        if not dispositivo_id or not estado:
            return Response(
                {'error': 'dispositivo_id y estado son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            dispositivo = Dispositivo.objects.get(id=dispositivo_id)
        except Dispositivo.DoesNotExist:
            return Response(
                {'error': 'Dispositivo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        evento = EventoOcupacion.objects.create(
            dispositivo=dispositivo,
            estado=estado
        )

        return Response(
            EventoOcupacionSerializer(evento).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], url_path='horas-pico')
    def horas_pico(self, request):
        """
        Estadística de horas pico de ocupación. (HU-12)
        Cuenta cuántas veces el laboratorio quedó "ocupado" en cada
        hora del día (0-23), opcionalmente filtrado por dispositivo
        o laboratorio y por rango de fechas.

        GET /api/v1/ocupacion/horas-pico/
        GET /api/v1/ocupacion/horas-pico/?dispositivo=1
        GET /api/v1/ocupacion/horas-pico/?desde=2026-06-01&hasta=2026-06-20
        """
        queryset = EventoOcupacion.objects.filter(estado='ocupado')

        dispositivo = request.query_params.get('dispositivo')
        desde       = request.query_params.get('desde')
        hasta       = request.query_params.get('hasta')

        if dispositivo:
            queryset = queryset.filter(dispositivo__id=dispositivo)
        if desde:
            queryset = queryset.filter(registrado_en__date__gte=desde)
        if hasta:
            queryset = queryset.filter(registrado_en__date__lte=hasta)

        conteo_por_hora = (
            queryset
            .annotate(hora=ExtractHour('registrado_en'))
            .values('hora')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        resultado = [
            {'hora': item['hora'], 'total_eventos_ocupado': item['total']}
            for item in conteo_por_hora
        ]

        return Response({
            'hora_pico': resultado[0] if resultado else None,
            'detalle_por_hora': resultado,
        })