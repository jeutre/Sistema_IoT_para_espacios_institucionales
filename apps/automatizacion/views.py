"""
apps/automatizacion/views.py
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
