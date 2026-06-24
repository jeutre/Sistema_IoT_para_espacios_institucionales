import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.equipos.models import EventoConexion
from apps.ocupacion.models import EventoOcupacion
from apps.dispositivos.models import HistorialComunicacion

class ExportarCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tipo):
        if tipo == 'conexion':
            return self.exportar_conexiones()
        elif tipo == 'ocupacion':
            return self.exportar_ocupacion()
        elif tipo == 'historial':
            return self.exportar_historial()
        return HttpResponse('Tipo no válido', status=400)

    def exportar_conexiones(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="eventos_conexion.csv"'
        writer = csv.writer(response)
        writer.writerow(['Equipo', 'IP', 'Tipo Evento', 'Fecha y Hora'])
        for evento in EventoConexion.objects.select_related('equipo').all():
            writer.writerow([evento.equipo.nombre, evento.equipo.ip, evento.get_tipo_display(), evento.registrado_en])
        return response

    def exportar_ocupacion(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="eventos_ocupacion.csv"'
        writer = csv.writer(response)
        writer.writerow(['Laboratorio', 'Dispositivo', 'Estado', 'Fecha y Hora'])
        for evento in EventoOcupacion.objects.select_related('dispositivo__laboratorio').all():
            writer.writerow([evento.dispositivo.laboratorio.nombre, evento.dispositivo.identificador, evento.get_estado_display(), evento.registrado_en])
        return response

    def exportar_historial(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="historial_mensajes.csv"'
        writer = csv.writer(response)
        writer.writerow(['Dispositivo', 'Mensaje', 'Recibido En'])
        for h in HistorialComunicacion.objects.select_related('dispositivo').all():
            writer.writerow([h.dispositivo.identificador, h.mensaje, h.recibido_en])
        return response
