"""
apps/automatizacion/views.py

CAMBIO: se agrega historial_automatizaciones() (HU-32), que faltaba por
completo. A diferencia de control/historial/ (HU-31, muestra TODOS los
comandos), este endpoint filtra solo los que origen='automatico' —
posible gracias al nuevo campo Comando.origen (ver apps/control/models.py).
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ReglaAutomatizacion
from .serializers import ReglaSerializer
from .servicios import evaluar_reglas


class ReglaAutomatizacionViewSet(viewsets.ModelViewSet):
    """
    CRUD de reglas de automatización. (HU-28)
    GET    /api/v1/automatizacion/reglas/
    POST   /api/v1/automatizacion/reglas/
    PUT    /api/v1/automatizacion/reglas/<id>/
    DELETE /api/v1/automatizacion/reglas/<id>/
    """
    serializer_class   = ReglaSerializer
    permission_classes = [IsAuthenticated]
    queryset           = ReglaAutomatizacion.objects.all()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_evaluacion(request):
    """
    Dispara el motor de reglas manualmente. (HU-28)
    Útil para pruebas desde Postman o el dashboard.
    POST /api/v1/automatizacion/evaluar/
    """
    try:
        resumen = evaluar_reglas()
        return Response({
            'mensaje':            'Evaluación completada.',
            'reglas_evaluadas':   resumen['reglas_evaluadas'],
            'reglas_omitidas_por_horario': resumen.get('reglas_omitidas_por_horario', 0),
            'comandos_esp32':     resumen['comandos_esp32'],
            'comandos_pc':        resumen['comandos_pc'],
            'comandos_fallidos':  resumen['comandos_fallidos'],
        })
    except Exception as e:
        return Response(
            {'error': f'Error durante la evaluación: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estado_scheduler(request):
    """
    Muestra si el scheduler está corriendo y cuándo es la próxima evaluación.
    GET /api/v1/automatizacion/scheduler/
    """
    try:
        from .scheduler import _scheduler

        if not _scheduler or not _scheduler.running:
            return Response({
                'corriendo':         False,
                'mensaje':           'El scheduler no está activo.',
                'proxima_ejecucion': None,
            })

        job = _scheduler.get_job('evaluar_reglas')
        proxima = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job and job.next_run_time else None

        return Response({
            'corriendo':         True,
            'proxima_ejecucion': proxima,
            'zona_horaria':      'America/Guayaquil',
            'mensaje':           'Scheduler activo y evaluando reglas automáticamente.',
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_automatizaciones(request):
    """
    Historial de comandos generados por el motor de automatización
    (origen='automatico'), filtrable por tipo de acción y fecha. (HU-32)
    GET /api/v1/automatizacion/historial/?tipo=apagar_luces&desde=..&hasta=..
    """
    from apps.control.models import Comando
    from apps.control.serializers import ComandoSerializer

    qs = Comando.objects.filter(origen='automatico').select_related('dispositivo', 'equipo')

    tipo = request.query_params.get('tipo')
    if tipo:
        qs = qs.filter(tipo_accion=tipo)

    desde = request.query_params.get('desde')
    if desde:
        qs = qs.filter(creado_en__date__gte=desde)

    hasta = request.query_params.get('hasta')
    if hasta:
        qs = qs.filter(creado_en__date__lte=hasta)

    qs = qs.exclude(estado='pendiente').order_by('-creado_en')

    return Response(ComandoSerializer(qs, many=True).data)
