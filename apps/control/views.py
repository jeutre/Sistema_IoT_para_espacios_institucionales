from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from .models import Comando
from .serializers import ComandoSerializer
from .servicios import enviar_comando_a_equipo
from apps.dispositivos.models import Dispositivo
from apps.equipos.models import Equipo


class ComandoViewSet(viewsets.ModelViewSet):
    serializer_class = ComandoSerializer

    def get_permissions(self):
        if self.action in ['pendientes', 'confirmar_ejecucion']:
            return [HasAPIKey()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Comando.objects.select_related('dispositivo', 'equipo').all()
        tipo   = self.request.query_params.get('tipo')
        estado = self.request.query_params.get('estado')
        desde  = self.request.query_params.get('desde')
        hasta  = self.request.query_params.get('hasta')

        if tipo:
            queryset = queryset.filter(tipo_accion=tipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if desde:
            queryset = queryset.filter(creado_en__date__gte=desde)
        if hasta:
            queryset = queryset.filter(creado_en__date__lte=hasta)

        return queryset

    # ── HU-19 — Suspender equipo PC manualmente ───────────────────────────────
    @action(detail=False, methods=['post'], url_path='suspender-equipo')
    def suspender_equipo(self, request):
        """
        Suspende un equipo PC específico. (HU-19)
        POST /api/v1/control/comandos/suspender-equipo/
        Body: { "equipo_id": 1 }
        """
        equipo_id = request.data.get('equipo_id')
        if not equipo_id:
            return Response(
                {'error': 'equipo_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            equipo = Equipo.objects.get(id=equipo_id, activo=True)
        except Equipo.DoesNotExist:
            return Response(
                {'error': 'Equipo no encontrado o inactivo.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cmd = enviar_comando_a_equipo(equipo, 'suspender_equipo')
        return Response({
            'equipo':    equipo.nombre,
            'ip':        equipo.ip,
            'estado':    cmd.estado,
            'resultado': cmd.resultado,
        }, status=status.HTTP_200_OK if cmd.estado == 'ejecutado' else status.HTTP_502_BAD_GATEWAY)

    # ── HU-20 — Apagar equipo PC manualmente ──────────────────────────────────
    @action(detail=False, methods=['post'], url_path='apagar-equipo')
    def apagar_equipo(self, request):
        """
        Apaga un equipo PC específico. (HU-20)
        POST /api/v1/control/comandos/apagar-equipo/
        Body: { "equipo_id": 1 }
        """
        equipo_id = request.data.get('equipo_id')
        if not equipo_id:
            return Response(
                {'error': 'equipo_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            equipo = Equipo.objects.get(id=equipo_id, activo=True)
        except Equipo.DoesNotExist:
            return Response(
                {'error': 'Equipo no encontrado o inactivo.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cmd = enviar_comando_a_equipo(equipo, 'apagar_equipo')
        return Response({
            'equipo':    equipo.nombre,
            'ip':        equipo.ip,
            'estado':    cmd.estado,
            'resultado': cmd.resultado,
        }, status=status.HTTP_200_OK if cmd.estado == 'ejecutado' else status.HTTP_502_BAD_GATEWAY)

    # ── HU-20B / HU-29 / HU-30 — Comandos para ESP32 ─────────────────────────
    @action(detail=False, methods=['get'], url_path='pendientes',
            permission_classes=[HasAPIKey])
    def pendientes(self, request):
        """
        El ESP32 consulta sus comandos pendientes. (HU-29, HU-30)
        GET /api/v1/control/comandos/pendientes/?identificador=ESP32-LAB-01
        """
        identificador = request.query_params.get('identificador')
        if not identificador:
            return Response(
                {'error': 'El parámetro identificador es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            dispositivo = Dispositivo.objects.get(identificador=identificador)
        except Dispositivo.DoesNotExist:
            return Response(
                {'error': 'Dispositivo no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        pendientes = Comando.objects.filter(
            dispositivo=dispositivo,
            estado='pendiente'
        ).order_by('creado_en')

        return Response(self.get_serializer(pendientes, many=True).data)

    @action(detail=True, methods=['post'], url_path='confirmar',
            permission_classes=[HasAPIKey])
    def confirmar_ejecucion(self, request, pk=None):
        """
        El ESP32 confirma si ejecutó el comando. (HU-29, HU-30)
        POST /api/v1/control/comandos/<id>/confirmar/
        Body: { "exito": true }
        """
        comando = self.get_object()
        if comando.estado != 'pendiente':
            return Response(
                {'error': f'El comando ya fue procesado: {comando.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        exito            = request.data.get('exito', True)
        comando.estado   = 'ejecutado' if exito else 'fallido'
        comando.ejecutado_en = timezone.now()
        comando.save()

        return Response({'mensaje': f'Comando marcado como {comando.estado}.'})

    @action(detail=False, methods=['get'], url_path='historial')
    def historial(self, request):
        """
        Historial de todos los comandos ejecutados. (HU-31)
        GET /api/v1/control/comandos/historial/
        """
        queryset = self.get_queryset().exclude(estado='pendiente')
        page     = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)