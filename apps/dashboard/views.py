from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.laboratorio.models import Laboratorio
from apps.equipos.models import Equipo
from apps.dispositivos.models import Dispositivo
from apps.ocupacion.models import EventoOcupacion
from django.db.models import Subquery, OuterRef

class DashboardResumenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        labs_totales = Laboratorio.objects.count()
        labs_activos = Laboratorio.objects.filter(activo=True).count()
        
        equipos_totales = Equipo.objects.count()
        equipos_conectados = Equipo.objects.filter(estado_conexion='activo').count()
        
        dispositivos_totales = Dispositivo.objects.count()
        dispositivos_conectados = Dispositivo.objects.filter(estado='conectado').count()

        # Ocupacion actual (optimizada)
        ultimos_eventos = EventoOcupacion.objects.filter(
            dispositivo=OuterRef('pk')
        ).order_by('-registrado_en')
        
        dispositivos_ocupacion = Dispositivo.objects.annotate(
            ultimo_estado=Subquery(ultimos_eventos.values('estado')[:1])
        )

        labs_ocupados = sum(1 for d in dispositivos_ocupacion if d.ultimo_estado == 'ocupado')

        return Response({
            'laboratorios': {
                'totales': labs_totales,
                'activos': labs_activos,
                'ocupados_actualmente': labs_ocupados
            },
            'equipos': {
                'totales': equipos_totales,
                'conectados': equipos_conectados,
                'desconectados': equipos_totales - equipos_conectados
            },
            'dispositivos': {
                'totales': dispositivos_totales,
                'conectados': dispositivos_conectados,
                'desconectados': dispositivos_totales - dispositivos_conectados
            }
        })
