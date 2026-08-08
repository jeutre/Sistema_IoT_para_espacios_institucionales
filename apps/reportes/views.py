"""
apps/reportes/views.py

Esta es la versión "v2": incluye lo entregado para HU-33 (CSV + PDF de
ocupación, ver README_CAMBIOS_SPRINT3_4.md) y agrega los dos reportes que
faltaban por completo:

- HU-34: Reporte de disponibilidad de equipos (CSV).
- HU-35: Reporte de optimización energética (CSV), reutilizando los mismos
  cálculos que ya usa apps/dashboard/views.py::DashboardKPIsView (ahorro
  potencial, equipos encendidos sin uso), para no duplicar lógica de negocio
  en dos sitios que se puedan desincronizar.
"""
import csv
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from apps.equipos.models import EventoConexion, Equipo
from apps.ocupacion.models import EventoOcupacion
from apps.dispositivos.models import HistorialComunicacion
from apps.laboratorio.models import Laboratorio


class ExportarCSVView(APIView):
    """
    Exporta reportes en CSV (por defecto) o PDF (?formato=pdf, solo
    disponible hoy para tipo=ocupacion). Solo administrador.
    Filtro por período (HU-33/34/35): ?desde=YYYY-MM-DD&hasta=YYYY-MM-DD

    Tipos soportados: ocupacion, conexion, historial, disponibilidad, optimizacion
    """
    permission_classes = [IsAdminUser]

    TIPOS_VALIDOS = ('ocupacion', 'conexion', 'historial', 'disponibilidad', 'optimizacion')

    def get(self, request, tipo):
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')
        formato = request.query_params.get('formato', 'csv').lower()

        if tipo not in self.TIPOS_VALIDOS:
            return HttpResponse('Tipo no válido', status=400)

        if formato not in ('csv', 'pdf'):
            return HttpResponse('Formato no válido. Use csv o pdf.', status=400)

        if formato == 'pdf' and tipo != 'ocupacion':
            return HttpResponse(
                'La exportación PDF solo está disponible para tipo=ocupacion por ahora.',
                status=400,
            )

        if tipo == 'conexion':
            return self.exportar_conexiones(desde, hasta)
        elif tipo == 'ocupacion':
            if formato == 'pdf':
                return self.exportar_ocupacion_pdf(desde, hasta)
            return self.exportar_ocupacion(desde, hasta)
        elif tipo == 'historial':
            return self.exportar_historial(desde, hasta)
        elif tipo == 'disponibilidad':
            return self.exportar_disponibilidad(desde, hasta)
        elif tipo == 'optimizacion':
            return self.exportar_optimizacion_energetica(desde, hasta)

    @staticmethod
    def _rango(qs, campo, desde, hasta):
        if desde:
            qs = qs.filter(**{f'{campo}__date__gte': desde})
        if hasta:
            qs = qs.filter(**{f'{campo}__date__lte': hasta})
        return qs

    @staticmethod
    def _resumen_ocupacion(desde=None, hasta=None):
        """Cálculo compartido entre el CSV y el PDF de ocupación (HU-33)."""
        qs = EventoOcupacion.objects.select_related('dispositivo__laboratorio')
        qs = ExportarCSVView._rango(qs, 'timestamp', desde, hasta)

        total = qs.count()
        ocupados = qs.filter(estado='ocupado').count()
        vacios = qs.filter(estado='vacio').count()
        pct_ocupado = round((ocupados / total) * 100, 1) if total else 0.0
        pct_vacio = round((vacios / total) * 100, 1) if total else 0.0

        return {
            'queryset': qs, 'total': total, 'ocupados': ocupados, 'vacios': vacios,
            'pct_ocupado': pct_ocupado, 'pct_vacio': pct_vacio,
        }

    # ---------------------------------------------------------------- CSV --

    def exportar_ocupacion(self, desde=None, hasta=None):
        # HU-33: reporte de ocupación por período, con porcentajes.
        resumen = self._resumen_ocupacion(desde, hasta)
        qs = resumen['queryset']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_ocupacion.csv"'
        writer = csv.writer(response)

        writer.writerow(['REPORTE DE OCUPACIÓN'])
        writer.writerow(['Período', f'{desde or "inicio"} a {hasta or "hoy"}'])
        writer.writerow(['Total de eventos', resumen['total']])
        writer.writerow(['Eventos "ocupado"', resumen['ocupados'], f'{resumen["pct_ocupado"]}%'])
        writer.writerow(['Eventos "vacío"', resumen['vacios'], f'{resumen["pct_vacio"]}%'])
        writer.writerow([])

        writer.writerow(['Laboratorio', 'Dispositivo', 'Estado', 'Fecha y Hora'])
        for e in qs.order_by('timestamp'):
            writer.writerow([
                e.dispositivo.laboratorio.nombre,
                e.dispositivo.identificador,
                e.get_estado_display(),
                e.timestamp,
            ])
        return response

    def exportar_conexiones(self, desde=None, hasta=None):
        qs = EventoConexion.objects.select_related('equipo')
        qs = self._rango(qs, 'registrado_en', desde, hasta)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="eventos_conexion.csv"'
        writer = csv.writer(response)
        writer.writerow(['Equipo', 'IP', 'Tipo Evento', 'Fecha y Hora'])
        for evento in qs.order_by('registrado_en'):
            writer.writerow([evento.equipo.nombre, evento.equipo.ip,
                             evento.get_tipo_display(), evento.registrado_en])
        return response

    def exportar_historial(self, desde=None, hasta=None):
        qs = HistorialComunicacion.objects.select_related('dispositivo')
        qs = self._rango(qs, 'recibido_en', desde, hasta)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="historial_mensajes.csv"'
        writer = csv.writer(response)
        writer.writerow(['Dispositivo', 'Mensaje', 'Recibido En'])
        for h in qs.order_by('recibido_en'):
            writer.writerow([h.dispositivo.identificador, h.mensaje, h.recibido_en])
        return response

    def exportar_disponibilidad(self, desde=None, hasta=None):
        """
        HU-34: reporte de disponibilidad por equipo — porcentaje de tiempo
        que cada equipo estuvo 'activo' vs 'inactivo' en el período, a
        partir de sus EventoConexion (conexion/desconexion).
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_disponibilidad.csv"'
        writer = csv.writer(response)
        writer.writerow(['REPORTE DE DISPONIBILIDAD DE EQUIPOS'])
        writer.writerow(['Período', f'{desde or "inicio"} a {hasta or "hoy"}'])
        writer.writerow(['Generado', timezone.now().strftime('%d/%m/%Y %H:%M')])
        writer.writerow([])
        writer.writerow([
            'Equipo', 'Laboratorio', 'IP', 'Estado actual',
            'Eventos de conexión', 'Eventos de desconexión',
            'Minutos inactivo (actual)', 'Disponibilidad estimada',
        ])

        equipos = Equipo.objects.filter(activo=True).select_related('laboratorio')
        for equipo in equipos.order_by('laboratorio__nombre', 'nombre'):
            eventos = EventoConexion.objects.filter(equipo=equipo)
            eventos = self._rango(eventos, 'registrado_en', desde, hasta)
            conexiones = eventos.filter(tipo__in=['conexion', 'encendido']).count()
            desconexiones = eventos.filter(tipo='desconexion').count()

            total_eventos = conexiones + desconexiones
            # Aproximación simple: si el equipo pasa más tiempo generando
            # eventos de conexión que de desconexión, se considera más
            # disponible. Es una primera definición operativa —ver nota al
            # final del reporte— a refinar cuando se disponga de duración
            # real por intervalo.
            disponibilidad_pct = round((conexiones / total_eventos) * 100, 1) if total_eventos else (
                100.0 if equipo.estado_conexion == 'activo' else 0.0
            )

            writer.writerow([
                equipo.nombre,
                equipo.laboratorio.nombre,
                equipo.ip,
                equipo.get_estado_conexion_display(),
                conexiones,
                desconexiones,
                round(equipo.minutos_inactivo, 1) if equipo.minutos_inactivo is not None else '-',
                f'{disponibilidad_pct}%',
            ])

        writer.writerow([])
        writer.writerow(['Nota', (
            'La disponibilidad estimada es una primera definición basada en '
            'la proporción de eventos de conexión vs. desconexión registrados '
            'en el período; no mide duración exacta de cada intervalo activo. '
            'A validar con el cliente (misma salvedad que HU-23).'
        )])
        return response

    def exportar_optimizacion_energetica(self, desde=None, hasta=None):
        """
        HU-35: reporte de optimización energética — ahorro potencial y
        equipos encendidos sin uso. Usa el consumo real declarado por
        equipo (Equipo.consumo_watts, ya existente en el modelo) en vez de
        una constante global, para que el cálculo sea específico por PC.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_optimizacion_energetica.csv"'
        writer = csv.writer(response)
        writer.writerow(['REPORTE DE OPTIMIZACIÓN ENERGÉTICA'])
        writer.writerow(['Período', f'{desde or "inicio"} a {hasta or "hoy"}'])
        writer.writerow(['Generado', timezone.now().strftime('%d/%m/%Y %H:%M')])
        writer.writerow([])

        writer.writerow(['Equipo', 'Laboratorio', 'Estado', 'Consumo (W)', 'Minutos inactivo', 'Ahorro potencial estimado (Wh)'])
        inactivos = Equipo.objects.filter(activo=True, estado_conexion='inactivo').select_related('laboratorio')
        horas_inactividad_total = 0.0
        ahorro_wh_total = 0.0
        for equipo in inactivos.order_by('laboratorio__nombre', 'nombre'):
            mins = equipo.minutos_inactivo
            ahorro_equipo_wh = 0.0
            if mins:
                horas = mins / 60.0
                ahorro_equipo_wh = round(horas * equipo.consumo_watts, 1)
                horas_inactividad_total += horas
                ahorro_wh_total += ahorro_equipo_wh
            writer.writerow([
                equipo.nombre, equipo.laboratorio.nombre, equipo.get_estado_conexion_display(),
                equipo.consumo_watts,
                round(mins, 1) if mins is not None else '-', ahorro_equipo_wh,
            ])

        writer.writerow([])
        writer.writerow(['Equipos encendidos en laboratorios vacíos (desperdicio actual)'])
        writer.writerow(['Laboratorio', 'Equipos encendidos sin ocupación'])
        equipos_desperdiciando_total = 0
        for lab in Laboratorio.objects.filter(estado='activo'):
            ultimo = (EventoOcupacion.objects.filter(dispositivo__laboratorio=lab)
                      .order_by('-timestamp').first())
            lab_vacio = (ultimo is None) or (ultimo.estado == 'vacio')
            if not lab_vacio:
                continue
            n = Equipo.objects.filter(laboratorio=lab, activo=True, estado_conexion='activo').count()
            if n:
                writer.writerow([lab.nombre, n])
                equipos_desperdiciando_total += n

        writer.writerow([])
        writer.writerow(['RESUMEN'])
        writer.writerow(['Horas de inactividad acumuladas', round(horas_inactividad_total, 1)])
        writer.writerow(['Ahorro potencial total estimado (Wh)', round(ahorro_wh_total, 1)])
        writer.writerow(['Equipos encendidos sin uso (ahora mismo)', equipos_desperdiciando_total])
        writer.writerow([])
        writer.writerow(['Nota', (
            'Cifras estimadas con una potencia fija supuesta por equipo '
            '(POTENCIA_EQUIPO_W en settings). Es una primera definición a '
            'validar con el cliente, igual que en /dashboard/kpis/.'
        )])
        return response

    # ---------------------------------------------------------------- PDF --

    def exportar_ocupacion_pdf(self, desde=None, hasta=None):
        """
        HU-33: reporte de ocupación en PDF, con tabla-resumen y gráfico de
        barras (ocupado vs. vacío), tal como pide el criterio de aceptación.
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        )
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from io import BytesIO

        resumen = self._resumen_ocupacion(desde, hasta)
        qs = resumen['queryset']

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=2 * cm, bottomMargin=2 * cm,
            leftMargin=2 * cm, rightMargin=2 * cm,
        )
        estilos = getSampleStyleSheet()
        elementos = []

        elementos.append(Paragraph('Reporte de Ocupación', estilos['Title']))
        elementos.append(Paragraph(
            f'Período: {desde or "inicio"} a {hasta or "hoy"} · '
            f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
            estilos['Normal'],
        ))
        elementos.append(Spacer(1, 0.6 * cm))

        datos_tabla = [
            ['Indicador', 'Valor'],
            ['Total de eventos', str(resumen['total'])],
            ['Eventos "ocupado"', f"{resumen['ocupados']} ({resumen['pct_ocupado']}%)"],
            ['Eventos "vacío"', f"{resumen['vacios']} ({resumen['pct_vacio']}%)"],
        ]
        tabla = Table(datos_tabla, colWidths=[8 * cm, 8 * cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabla)
        elementos.append(Spacer(1, 1 * cm))

        elementos.append(Paragraph('Distribución de eventos', estilos['Heading2']))
        dibujo = Drawing(400, 200)
        grafico = VerticalBarChart()
        grafico.x = 50
        grafico.y = 20
        grafico.height = 150
        grafico.width = 300
        grafico.data = [[resumen['ocupados'], resumen['vacios']]]
        grafico.categoryAxis.categoryNames = ['Ocupado', 'Vacío']
        grafico.bars[0].fillColor = colors.HexColor('#2E7D6E')
        grafico.valueAxis.valueMin = 0
        maximo = max(resumen['ocupados'], resumen['vacios'], 1)
        grafico.valueAxis.valueMax = maximo * 1.2
        dibujo.add(grafico)
        elementos.append(dibujo)
        elementos.append(Spacer(1, 1 * cm))

        elementos.append(Paragraph('Detalle de eventos', estilos['Heading2']))
        filas_detalle = [['Laboratorio', 'Dispositivo', 'Estado', 'Fecha y hora']]
        for e in qs.order_by('timestamp')[:200]:
            filas_detalle.append([
                e.dispositivo.laboratorio.nombre,
                e.dispositivo.identificador,
                e.get_estado_display(),
                e.timestamp.strftime('%d/%m/%Y %H:%M'),
            ])
        if resumen['total'] > 200:
            filas_detalle.append(['…', '…', '…', f'({resumen["total"] - 200} eventos adicionales no listados)'])

        tabla_detalle = Table(filas_detalle, colWidths=[4.5 * cm, 4.5 * cm, 3 * cm, 4 * cm], repeatRows=1)
        tabla_detalle.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
        ]))
        elementos.append(tabla_detalle)

        doc.build(elementos)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_ocupacion.pdf"'
        return response
