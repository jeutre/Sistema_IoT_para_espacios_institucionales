from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Alerta
from .serializers import AlertaSerializer


class AlertaViewSet(viewsets.ModelViewSet):
    """
    Historial de alertas (HU-27). Filtros disponibles:
      ?tipo=desconexion|movimiento|equipo_sin_ocupacion|error_sistema
      ?nivel=bajo|medio|critico
      ?leida=true|false
      ?desde=YYYY-MM-DD   ?hasta=YYYY-MM-DD   (por fecha de creación)
    """
    serializer_class = AlertaSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = Alerta.objects.all()
        p = self.request.query_params

        tipo = p.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)

        nivel = p.get('nivel')
        if nivel:
            qs = qs.filter(nivel=nivel)

        leida = p.get('leida')
        if leida is not None:
            qs = qs.filter(leida=leida.lower() == 'true')

        desde = p.get('desde')
        if desde:
            qs = qs.filter(creado_en__date__gte=desde)

        hasta = p.get('hasta')
        if hasta:
            qs = qs.filter(creado_en__date__lte=hasta)

        return qs