from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Equipo
from .serializers import EquipoSerializer


class EquipoViewSet(viewsets.ModelViewSet):
    serializer_class   = EquipoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset    = Equipo.objects.all()
        laboratorio = self.request.query_params.get('laboratorio')
        activo      = self.request.query_params.get('activo')

        if laboratorio:
            queryset = queryset.filter(laboratorio__id=laboratorio)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')

        return queryset