"""
apps/control/views.py

CAMBIOS (Hallazgo crítico 2 del informe de avance — HU-20B):

1. Se agrega la acción encender_equipo(): endpoint manual para que el
   administrador ordene, desde el dashboard, el encendido de un equipo con
   relay (Comando model.tipo_accion='encender_relay'). No existía ningún
   endpoint equivalente a suspender-equipo/apagar-equipo para esto.

2. confirmar_ejecucion() ahora actualiza Equipo.estado_conexion y registra
   un EventoConexion cuando el ESP32 confirma que ejecutó un comando de
   'encender_relay' sobre un equipo — antes el ping periódico (HU-14) era
   la única forma de que el sistema se enterara de que el equipo volvió a
   estar activo, lo que podía tardar hasta 2 minutos.

3. Todos los comandos creados desde este archivo (disparados por un
   administrador) se marcan con origen='manual', para distinguirlos en el
   historial de los que dispara el motor de automatización (HU-31 vs HU-32).
"""
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
from apps.equipos.models import EventoConexion


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
        origen = self.request.query_params.get('origen')
        desde  = self.request.query_params.get('desde')
        hasta  = self.request.query_params.get('hasta')

        if tipo:
            queryset = queryset.filter(tipo_accion=tipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if origen:
            queryset = queryset.filter(origen=origen)
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

        cmd = enviar_comando_a_equipo(equipo, 'suspender_equipo', origen='manual')
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

        cmd = enviar_comando_a_equipo(equipo, 'apagar_equipo', origen='manual')
        return Response({
            'equipo':    equipo.nombre,
            'ip':        equipo.ip,
            'estado':    cmd.estado,
            'resultado': cmd.resultado,
        }, status=status.HTTP_200_OK if cmd.estado == 'ejecutado' else status.HTTP_502_BAD_GATEWAY)

    # ── HU-20B — Encender equipo por relay manualmente ────────────────────────
    @action(detail=False, methods=['post'], url_path='encender-equipo')
    def encender_equipo(self, request):
        """
        Ordena el encendido de un equipo PC vía el relay de su ESP32. (HU-20B ★)
        A diferencia de suspender/apagar (que van directo al agente Windows por
        HTTP), el relay lo controla el ESP32: este endpoint encola un Comando
        pendiente que el ESP32 recogerá en su próximo sondeo a /pendientes/ y
        confirmará en /<id>/confirmar/.

        POST /api/v1/control/comandos/encender-equipo/
        Body: { "equipo_id": 1 }
        """
        equipo_id = request.data.get('equipo_id')
        if not equipo_id:
            return Response(
                {'error': 'equipo_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            equipo = Equipo.objects.select_related('laboratorio').get(id=equipo_id, activo=True)
        except Equipo.DoesNotExist:
            return Response(
                {'error': 'Equipo no encontrado o inactivo.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not equipo.tiene_relay or equipo.relay_gpio is None:
            return Response(
                {'error': 'Este equipo no tiene un relay configurado; no se puede encender de forma remota.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        dispositivo = Dispositivo.objects.filter(
            laboratorio=equipo.laboratorio, estado='conectado'
        ).first()
        if not dispositivo:
            return Response(
                {'error': 'No hay un ESP32 conectado en el laboratorio de este equipo.'},
                status=status.HTTP_409_CONFLICT
            )

        ya_pendiente = Comando.objects.filter(
            equipo=equipo, tipo_accion='encender_relay', estado='pendiente'
        ).exists()
        if ya_pendiente:
            return Response({
                'equipo': equipo.nombre,
                'estado': 'pendiente',
                'mensaje': 'Ya existe una orden de encendido pendiente para este equipo.',
            }, status=status.HTTP_200_OK)

        comando = Comando.objects.create(
            dispositivo=dispositivo,
            equipo=equipo,
            tipo_accion='encender_relay',
            origen='manual',
        )

        return Response({
            'equipo': equipo.nombre,
            'esp32': dispositivo.identificador,
            'gpio': equipo.relay_gpio,
            'comando_id': comando.id,
            'estado': comando.estado,
            'mensaje': 'Orden de encendido encolada; el ESP32 la ejecutará en su próximo sondeo.',
        }, status=status.HTTP_201_CREATED)

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
        El ESP32 confirma si ejecutó el comando. (HU-29, HU-30, HU-20B)
        POST /api/v1/control/comandos/<id>/confirmar/
        Body: { "exito": true }
        """
        comando = self.get_object()
        if comando.estado != 'pendiente':
            return Response(
                {'error': f'El comando ya fue procesado: {comando.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        exito                 = request.data.get('exito', True)
        comando.estado        = 'ejecutado' if exito else 'fallido'
        comando.ejecutado_en  = timezone.now()
        comando.save()

        # Si era una orden de encendido por relay sobre un Equipo y salió
        # bien, reflejarlo de inmediato (no esperar al próximo ping/HU-14).
        if exito and comando.tipo_accion == 'encender_relay' and comando.equipo_id:
            equipo = comando.equipo
            estado_previo = equipo.estado_conexion
            equipo.estado_conexion = 'activo'
            equipo.ultima_actividad = timezone.now()
            equipo.save(update_fields=['estado_conexion', 'ultima_actividad', 'actualizado_en'])
            if estado_previo != 'activo':
                EventoConexion.objects.create(equipo=equipo, tipo='encendido')

        return Response({'mensaje': f'Comando marcado como {comando.estado}.'})

    @action(detail=False, methods=['get'], url_path='historial')
    def historial(self, request):
        """
        Historial de todos los comandos ejecutados, manuales y automáticos.
        (HU-31). Para ver SOLO los automáticos, usar HU-32
        (/api/v1/automatizacion/historial/) o el filtro ?origen=automatico.
        GET /api/v1/control/comandos/historial/
        """
        queryset = self.get_queryset().exclude(estado='pendiente')
        page     = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)
