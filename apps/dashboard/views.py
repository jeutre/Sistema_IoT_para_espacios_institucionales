from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from apps.laboratorio.models import Laboratorio
from apps.equipos.models import Equipo
from apps.dispositivos.models import Dispositivo
from apps.ocupacion.models import EventoOcupacion
from django.db.models import Subquery, OuterRef

class DashboardResumenView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        labs_totales = Laboratorio.objects.count()
        labs_activos = Laboratorio.objects.filter(estado='activo').count()

        equipos_totales = Equipo.objects.count()
        equipos_conectados = Equipo.objects.filter(estado_conexion='activo').count()

        dispositivos_totales = Dispositivo.objects.count()
        dispositivos_conectados = Dispositivo.objects.filter(estado='conectado').count()

        # Ocupacion actual (optimizada)
        ultimos_eventos = EventoOcupacion.objects.filter(
            dispositivo=OuterRef('pk')
        ).order_by('-timestamp')

        dispositivos_ocupacion = Dispositivo.objects.annotate(
            ultimo_estado=Subquery(ultimos_eventos.values('estado')[:1])
        )

        labs_ocupados = sum(1 for d in dispositivos_ocupacion if d.ultimo_estado == 'ocupado')
        # Disponibilidad en tiempo real: laboratorios activos que NO están ocupados. (HU-21)
        labs_disponibles = max(labs_activos - labs_ocupados, 0)

        return Response({
            'laboratorios': {
                'totales': labs_totales,
                'activos': labs_activos,
                'ocupados_actualmente': labs_ocupados,
                'disponibles_actualmente': labs_disponibles
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


class DashboardKPIsView(APIView):
    """
    KPIs institucionales (HU-23). Solo administrador.
    Período opcional: ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD (por defecto últimos 7 días).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        from datetime import timedelta
        from django.conf import settings
        from django.utils import timezone

        hasta = request.query_params.get('hasta')
        desde = request.query_params.get('desde')

        eventos = EventoOcupacion.objects.all()
        if desde:
            eventos = eventos.filter(timestamp__date__gte=desde)
        if hasta:
            eventos = eventos.filter(timestamp__date__lte=hasta)
        if not desde and not hasta:
            eventos = eventos.filter(timestamp__gte=timezone.now() - timedelta(days=7))

        total_ev = eventos.count()
        ocupados = eventos.filter(estado='ocupado').count()
        porcentaje_ocupacion = round((ocupados / total_ev) * 100, 1) if total_ev else 0.0

        equipos_totales = Equipo.objects.filter(activo=True).count()
        equipos_activos = Equipo.objects.filter(activo=True, estado_conexion='activo').count()
        disponibilidad_equipos = round((equipos_activos / equipos_totales) * 100, 1) if equipos_totales else 0.0

        inactivos = [e for e in Equipo.objects.filter(activo=True, estado_conexion='inactivo')]
        minutos = [e.minutos_inactivo for e in inactivos if e.minutos_inactivo is not None]
        tiempo_promedio_inactividad_min = round(sum(minutos) / len(minutos), 1) if minutos else 0.0

        # Ahorro energético potencial (HU-23)
        potencia_w = getattr(settings, 'POTENCIA_EQUIPO_W', 150)
        inactivos_ahorro = Equipo.objects.filter(activo=True, estado_conexion='inactivo')
        horas_inactividad_total = 0.0
        ahorro_wh = 0.0
        for e in inactivos_ahorro:
            mins = e.minutos_inactivo
            if mins:
                horas = mins / 60.0
                horas_inactividad_total += horas
                ahorro_wh += horas * potencia_w

        # Equipos encendidos en laboratorios vacíos (desperdicio actual)
        equipos_desperdiciando = 0
        for lab in Laboratorio.objects.filter(estado='activo'):
            ultimo = (EventoOcupacion.objects.filter(dispositivo__laboratorio=lab)
                      .order_by('-timestamp').first())
            lab_vacio = (ultimo is None) or (ultimo.estado == 'vacio')
            if lab_vacio:
                equipos_desperdiciando += Equipo.objects.filter(
                    laboratorio=lab, activo=True, estado_conexion='activo'
                ).count()

        eficiencia_operativa = porcentaje_ocupacion

        return Response({
            'periodo': {'desde': desde or 'últimos 7 días', 'hasta': hasta or 'hoy'},
            'porcentaje_ocupacion': porcentaje_ocupacion,
            'disponibilidad_equipos': disponibilidad_equipos,
            'tiempo_promedio_inactividad_min': tiempo_promedio_inactividad_min,
            'ahorro_energetico': {
                'horas_inactividad_total': round(horas_inactividad_total, 1),
                'potencia_supuesta_w': potencia_w,
                'ahorro_potencial_wh': round(ahorro_wh, 1),
                'equipos_encendidos_sin_uso': equipos_desperdiciando,
            },
            'eficiencia_operativa': eficiencia_operativa,
            '_nota': 'ahorro_energetico y eficiencia_operativa son una primera definición a validar con el cliente.',
        })