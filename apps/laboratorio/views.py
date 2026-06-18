from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Laboratorio
from .serializers import LaboratorioSerializer


class LaboratorioViewSet(viewsets.ModelViewSet):
    serializer_class   = LaboratorioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
       
        queryset = Laboratorio.objects.all()
        activo   = self.request.query_params.get('activo')
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        return queryset

    @action(detail=True, methods=['patch'], url_path='toggle-activo')
    def toggle_activo(self, request, pk=None):
       
        laboratorio = self.get_object()
        laboratorio.activo = not laboratorio.activo
        laboratorio.save()
        estado = 'activado' if laboratorio.activo else 'desactivado'
        return Response(
            {'mensaje': f'Laboratorio {estado} correctamente.', 'activo': laboratorio.activo},
            status=status.HTTP_200_OK
        )