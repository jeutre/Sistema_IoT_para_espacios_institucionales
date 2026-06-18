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
        queryset    = EventoOcupacion.objects.all()
        dispositivo = self.request.query_params.get('dispositivo')
        if dispositivo:
            queryset = queryset.filter(dispositivo__id=dispositivo)
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
