from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from .models import Comando
from .serializers import ComandoSerializer
from apps.dispositivos.models import Dispositivo

class ComandoViewSet(viewsets.ModelViewSet):
    serializer_class = ComandoSerializer
    
    def get_permissions(self):
        # El ESP32 consume pendientes y confirmar_ejecucion
        if self.action in ['pendientes', 'confirmar_ejecucion']:
            return [HasAPIKey()]
        # El frontend agenda comandos y ve historial
        return [IsAuthenticated()]

    def get_queryset(self):
        return Comando.objects.all()

    @action(detail=False, methods=['get'], url_path='pendientes/(?P<mac>[^/.]+)')
    def pendientes(self, request, mac=None):
        try:
            dispositivo = Dispositivo.objects.get(mac_address=mac)
        except Dispositivo.DoesNotExist:
            return Response({'error': 'Dispositivo no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        pendientes = Comando.objects.filter(dispositivo=dispositivo, estado='pendiente')
        serializer = self.get_serializer(pendientes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='confirmar')
    def confirmar_ejecucion(self, request, pk=None):
        comando = self.get_object()
        exito = request.data.get('exito', True)
        
        comando.estado = 'ejecutado' if exito else 'fallido'
        comando.ejecutado_en = timezone.now()
        comando.save()
        
        return Response({'mensaje': f"Comando marcado como {comando.estado}"})
