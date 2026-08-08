"""
Aceptación — ÉPICA 9: Reportes (completo).
HU-33 Ocupación (CSV+PDF) · HU-34 Disponibilidad de equipos · HU-35
Optimización energética.

Esta es la versión "v2" de este archivo: agrega las pruebas de HU-34 y
HU-35 sobre las que ya se entregaron para HU-33 en el paquete de Sprint 1-2.
"""
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from apps.acceptance_base import AcceptanceBase
from apps.equipos.models import Equipo


class ReportesTests(AcceptanceBase):

    def _generar_evento_ocupacion(self, lab_id=None):
        lab_id = lab_id or self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        r = self.esp32_reporta_pir(disp_id, 'ocupado')
        assert r.status_code in (200, 201), f'esp32_reporta_pir falló: {r.status_code} {r.data}'
        return lab_id, disp_id

    # ---------------- Permisos ----------------

    def test_reportes_requiere_admin(self):
        self.as_no_admin()
        r = self.client.get('/api/v1/reportes/exportar/ocupacion/')
        self.assertIn(r.status_code, (403, 401))

    def test_reportes_anonimo_rechazado(self):
        self.as_anon()
        r = self.client.get('/api/v1/reportes/exportar/ocupacion/')
        self.assertIn(r.status_code, (403, 401))

    def test_reportes_tipo_invalido(self):
        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/no-existe/')
        self.assertEqual(r.status_code, 400)

    # ---------------- HU-33 — CSV ocupación ----------------

    def test_hu33_csv_ocupacion_contiene_encabezado(self):
        self._generar_evento_ocupacion()
        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/ocupacion/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'text/csv')
        contenido = b''.join(r.streaming_content) if r.streaming else r.content
        self.assertIn(b'REPORTE DE OCUPACI', contenido)

    def test_hu33_csv_ocupacion_filtra_por_fecha(self):
        self._generar_evento_ocupacion()
        self.as_admin()
        ayer = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.get(f'/api/v1/reportes/exportar/ocupacion/?desde={ayer}&hasta={ayer}')
        self.assertEqual(r.status_code, 200)
        contenido = b''.join(r.streaming_content) if r.streaming else r.content
        self.assertIn(b'Total de eventos,0', contenido.replace(b'\r\n', b'\n'))

    @patch('apps.equipos.views.ejecutar_ping', return_value=True)
    def test_hu33_csv_conexiones(self, _mock):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.80', mac='AA:BB:CC:00:01:00')
        self.as_admin()
        self.client.get(f'/api/v1/equipos/{eq_id}/ping/')
        r = self.client.get('/api/v1/reportes/exportar/conexion/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'text/csv')

    def test_hu33_csv_historial(self):
        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/historial/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'text/csv')

    # ---------------- HU-33 — PDF ocupación ----------------

    def test_hu33_pdf_ocupacion_se_genera(self):
        self._generar_evento_ocupacion()
        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/ocupacion/?formato=pdf')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'application/pdf')
        contenido = b''.join(r.streaming_content) if r.streaming else r.content
        self.assertTrue(contenido.startswith(b'%PDF'))

    def test_hu33_pdf_no_disponible_para_otros_tipos(self):
        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/conexion/?formato=pdf')
        self.assertEqual(r.status_code, 400)

    def test_hu33_formato_invalido_rechazado(self):
        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/ocupacion/?formato=excel')
        self.assertEqual(r.status_code, 400)

    # ---------------- HU-34 — Disponibilidad de equipos ----------------

    @patch('apps.equipos.views.ejecutar_ping', return_value=True)
    def test_hu34_disponibilidad_incluye_equipo(self, _mock):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.110', mac='AA:BB:CC:00:04:00')
        self.as_admin()
        self.client.get(f'/api/v1/equipos/{eq_id}/ping/')  # genera EventoConexion tipo=conexion

        r = self.client.get('/api/v1/reportes/exportar/disponibilidad/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'text/csv')
        contenido = b''.join(r.streaming_content) if r.streaming else r.content
        equipo = Equipo.objects.get(id=eq_id)
        self.assertIn(equipo.nombre.encode(), contenido)

    def test_hu34_disponibilidad_respeta_filtro_de_fechas(self):
        self.as_admin()
        ayer = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.get(f'/api/v1/reportes/exportar/disponibilidad/?desde={ayer}&hasta={ayer}')
        self.assertEqual(r.status_code, 200)

    # ---------------- HU-35 — Optimización energética ----------------

    def test_hu35_optimizacion_incluye_equipo_inactivo(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.111', mac='AA:BB:CC:00:04:01')
        equipo = Equipo.objects.get(id=eq_id)
        equipo.estado_conexion = 'inactivo'
        equipo.ultima_actividad = timezone.now() - timedelta(hours=2)
        equipo.consumo_watts = 200.0
        equipo.save(update_fields=['estado_conexion', 'ultima_actividad', 'consumo_watts'])

        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/optimizacion/')
        self.assertEqual(r.status_code, 200)
        contenido = b''.join(r.streaming_content) if r.streaming else r.content
        self.assertIn(equipo.nombre.encode(), contenido)
        self.assertIn(b'RESUMEN', contenido)

    def test_hu35_optimizacion_detecta_laboratorio_vacio_con_equipos_encendidos(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.112', mac='AA:BB:CC:00:04:02')
        equipo = Equipo.objects.get(id=eq_id)
        equipo.estado_conexion = 'activo'
        equipo.save(update_fields=['estado_conexion'])
        # No se reporta ningún evento PIR 'ocupado' -> laboratorio se considera vacío.

        self.as_admin()
        r = self.client.get('/api/v1/reportes/exportar/optimizacion/')
        self.assertEqual(r.status_code, 200)
        contenido = b''.join(r.streaming_content) if r.streaming else r.content
        self.assertIn('desperdicio'.encode(), contenido)
