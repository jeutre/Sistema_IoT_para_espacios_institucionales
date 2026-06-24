from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ReglaAutomatizacion
from .serializers import ReglaSerializer
from .servicios import evaluar_reglas

class ReglaAutomatizacionViewSet(viewsets.ModelViewSet):
    serializer_class = ReglaSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReglaAutomatizacion.objects.all()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_evaluacion(request):
    """
    Endpoint manual para ejecutar el motor de reglas (útil para Cron jobs externos).
    """
    comandos = evaluar_reglas()
    return Response({'mensaje': f'Evaluación completada. Se generaron {comandos} comandos.'})
