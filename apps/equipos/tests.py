"""
Aceptación — ÉPICA 5: Equipos IPv4.
HU-13 Registrar IPv4 · HU-13B Registrar MAC · HU-14 Ping · HU-15 Activos ·
HU-16 Inactivos · HU-17 Eventos conexión/desconexión · HU-18 Historial.

El ping físico se sustituye por un doble (equipo encendido / apagado); ruta,
endpoint y respuesta son los reales.
"""
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from apps.acceptance_base import AcceptanceBase


class EquipoTests(AcceptanceBase):

    # ---------------- HU-13 — Registrar IPv4 ----------------

    def test_hu13_registrar_ipv4_valida(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.51', mac='AA:BB:CC:00:00:01')
        self.assertIsNotNone(eq_id)

    def test_hu13_rechaza_ipv6(self):
        lab_id = self.crear_laboratorio()
        self.as_admin()
        r = self.client.post('/api/v1/equipos/', {
            'laboratorio': lab_id, 'nombre': 'PC-IPv6',
            'ip': '2001:db8::1', 'mac': 'AA:BB:CC:00:00:02',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_hu13_rechaza_ip_malformada(self):
        lab_id = self.crear_laboratorio()
        self.as_admin()
        r = self.client.post('/api/v1/equipos/', {
            'laboratorio': lab_id, 'nombre': 'PC-mala',
            'ip': '999.10.10.10', 'mac': 'AA:BB:CC:00:00:03',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    # ---------------- HU-13B — Registrar MAC ----------------

    def test_hu13b_rechaza_mac_invalida(self):
        lab_id = self.crear_laboratorio()
        self.as_admin()
        r = self.client.post('/api/v1/equipos/', {
            'laboratorio': lab_id, 'nombre': 'PC-mac',
            'ip': '192.168.1.52', 'mac': 'NO-ES-MAC',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    def test_hu13b_mac_duplicada_rechazada(self):
        lab_id = self.crear_laboratorio()
        self.registrar_equipo(lab_id, nombre='PC-A', ip='192.168.1.53', mac='AA:BB:CC:00:00:04')
        self.as_admin()
        r = self.client.post('/api/v1/equipos/', {
            'laboratorio': lab_id, 'nombre': 'PC-B',
            'ip': '192.168.1.54', 'mac': 'AA:BB:CC:00:00:04',
        }, format='json')
        self.assertEqual(r.status_code, 400)

    # ---------------- HU-14 — Ping ----------------

    @patch('apps.equipos.views.ejecutar_ping', return_value=True)
    def test_hu14_ping_equipo_encendido(self, _mock):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.55', mac='AA:BB:CC:00:00:05')
        self.as_admin()
        r = self.client.get(f'/api/v1/equipos/{eq_id}/ping/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data['responde'])
        self.assertEqual(r.data['estado_conexion'], 'activo')

    # ---------------- HU-15 — Activos ----------------

    @patch('apps.equipos.views.ejecutar_ping', return_value=True)
    def test_hu15_equipo_encendido_aparece_en_activos(self, _mock):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.56', mac='AA:BB:CC:00:00:06')
        self.as_admin()
        self.client.get(f'/api/v1/equipos/{eq_id}/ping/')      # detecta que responde
        r = self.client.get('/api/v1/equipos/?estado=activo')
        ids = [e['id'] for e in r.data.get('results', r.data)]
        self.assertIn(eq_id, ids)

    # ---------------- HU-16 — Inactivos ----------------

    @patch('apps.equipos.views.ejecutar_ping', return_value=False)
    def test_hu16_equipo_apagado_aparece_en_inactivos(self, _mock):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.57', mac='AA:BB:CC:00:00:07')
        self.as_admin()
        self.client.get(f'/api/v1/equipos/{eq_id}/ping/')      # no responde
        r = self.client.get('/api/v1/equipos/?estado=inactivo')
        ids = [e['id'] for e in r.data.get('results', r.data)]
        self.assertIn(eq_id, ids)

    # ---------------- HU-17 — Eventos conexión/desconexión ----------------

    def test_hu17_registra_conexion_y_desconexion(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.58', mac='AA:BB:CC:00:00:08')
        self.as_admin()
        # 1) el equipo responde -> evento de conexión
        with patch('apps.equipos.views.ejecutar_ping', return_value=True):
            self.client.get(f'/api/v1/equipos/{eq_id}/ping/')
        # 2) el equipo deja de responder -> evento de desconexión
        with patch('apps.equipos.views.ejecutar_ping', return_value=False):
            self.client.get(f'/api/v1/equipos/{eq_id}/ping/')

        r = self.client.get(f'/api/v1/equipos/eventos-conexion/?equipo={eq_id}')
        tipos = [e['tipo'] for e in r.data.get('results', r.data)]
        self.assertIn('conexion', tipos)
        self.assertIn('desconexion', tipos)

    def test_hu17_no_duplica_evento_si_no_cambia_estado(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.59', mac='AA:BB:CC:00:00:09')
        self.as_admin()
        with patch('apps.equipos.views.ejecutar_ping', return_value=True):
            self.client.get(f'/api/v1/equipos/{eq_id}/ping/')
            self.client.get(f'/api/v1/equipos/{eq_id}/ping/')  # mismo estado, no debe duplicar
        r = self.client.get(f'/api/v1/equipos/eventos-conexion/?equipo={eq_id}')
        datos = r.data.get('results', r.data)
        self.assertEqual(len(datos), 1)

    # ---------------- HU-18 — Historial de actividad ----------------

    def test_hu18_historial_del_equipo(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.60', mac='AA:BB:CC:00:00:0A')
        self.as_admin()
        with patch('apps.equipos.views.ejecutar_ping', return_value=True):
            self.client.get(f'/api/v1/equipos/{eq_id}/ping/')
        r = self.client.get(f'/api/v1/equipos/{eq_id}/historial/')
        self.assertEqual(r.status_code, 200)
        datos = r.data.get('results', r.data)
        self.assertGreaterEqual(len(datos), 1)

    def test_hu18_historial_rango_pasado_vacio(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.63', mac='AA:BB:CC:00:00:0B')
        self.as_admin()
        with patch('apps.equipos.views.ejecutar_ping', return_value=True):
            self.client.get(f'/api/v1/equipos/{eq_id}/ping/')
        ayer = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.get(f'/api/v1/equipos/{eq_id}/historial/?desde={ayer}&hasta={ayer}')
        datos = r.data.get('results', r.data)
        self.assertEqual(len(datos), 0)