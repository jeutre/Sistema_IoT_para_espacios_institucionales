from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Laboratorio
from .serializers import LaboratorioSerializer


class LaboratorioViewSet(viewsets.ModelViewSet):
    serializer_class   = LaboratorioSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Laboratorio.objects.all()
        estado   = self.request.query_params.get('estado')
        if estado in ('activo', 'inactivo', 'mantenimiento'):
            queryset = queryset.filter(estado=estado)
        # Compatibilidad legacy: ?activo=true|false
        activo = self.request.query_params.get('activo')
        if activo is not None:
            queryset = queryset.filter(estado='activo' if activo.lower() == 'true' else 'inactivo')
        return queryset

    @action(detail=True, methods=['patch'], url_path='toggle-activo')
    def toggle_activo(self, request, pk=None):
        """Alterna el estado del laboratorio entre 'activo' e 'inactivo'."""
        laboratorio = self.get_object()
        laboratorio.estado = 'inactivo' if laboratorio.estado == 'activo' else 'activo'
        laboratorio.save(update_fields=['estado', 'actualizado_en'])
        activo = laboratorio.estado == 'activo'
        mensaje = 'activado' if activo else 'desactivado'
        return Response(
            {'mensaje': f'Laboratorio {mensaje} correctamente.',
             'estado': laboratorio.estado,
             'activo': activo},
            status=status.HTTP_200_OK
        )