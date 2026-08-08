"""
Aceptación — ÉPICA 5 (control remoto) y HU-20B ★.
HU-19 Suspender · HU-20 Apagar · HU-20B Encender por relay ·
HU-31 Historial de comandos.

Este archivo estaba vacío en el repositorio original.
"""
from unittest.mock import patch
from apps.acceptance_base import AcceptanceBase
from apps.equipos.models import Equipo
from apps.control.models import Comando


class ControlTests(AcceptanceBase):

    def _equipo_con_relay(self, lab_id, **kwargs):
        eq_id = self.registrar_equipo(lab_id, **kwargs)
        equipo = Equipo.objects.get(id=eq_id)
        equipo.tiene_relay = True
        equipo.relay_gpio = 4
        equipo.estado_conexion = 'inactivo'
        equipo.save(update_fields=['tiene_relay', 'relay_gpio', 'estado_conexion'])
        return equipo

    # ---------------- HU-19 — Suspender ----------------

    @patch('apps.control.servicios.requests.post')
    def test_hu19_suspender_equipo(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'exito': True, 'mensaje': 'Suspendido'}

        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.100', mac='AA:BB:CC:00:03:00')
        self.as_admin()
        r = self.client.post('/api/v1/control/comandos/suspender-equipo/', {'equipo_id': eq_id}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['estado'], 'ejecutado')
        cmd = Comando.objects.get(equipo_id=eq_id, tipo_accion='suspender_equipo')
        self.assertEqual(cmd.origen, 'manual')

    def test_hu19_requiere_equipo_id(self):
        self.as_admin()
        r = self.client.post('/api/v1/control/comandos/suspender-equipo/', {}, format='json')
        self.assertEqual(r.status_code, 400)

    # ---------------- HU-20 — Apagar ----------------

    @patch('apps.control.servicios.requests.post')
    def test_hu20_apagar_equipo(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'exito': True, 'mensaje': 'Apagado'}

        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.101', mac='AA:BB:CC:00:03:01')
        self.as_admin()
        r = self.client.post('/api/v1/control/comandos/apagar-equipo/', {'equipo_id': eq_id}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['estado'], 'ejecutado')

    @patch('apps.control.servicios.requests.post')
    def test_hu20_agente_no_responde_devuelve_fallido(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.102', mac='AA:BB:CC:00:03:02')
        self.as_admin()
        r = self.client.post('/api/v1/control/comandos/apagar-equipo/', {'equipo_id': eq_id}, format='json')
        self.assertEqual(r.status_code, 502)
        self.assertEqual(r.data['estado'], 'fallido')

    # ---------------- HU-20B ★ — Encender por relay (manual) ----------------

    def test_hu20b_encender_equipo_sin_relay_rechazado(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.103', mac='AA:BB:CC:00:03:03')
        self.as_admin()
        r = self.client.post('/api/v1/control/comandos/encender-equipo/', {'equipo_id': eq_id}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_hu20b_encender_equipo_sin_esp32_conectado(self):
        lab_id = self.crear_laboratorio()
        equipo = self._equipo_con_relay(lab_id, ip='192.168.1.104', mac='AA:BB:CC:00:03:04')
        self.as_admin()
        r = self.client.post('/api/v1/control/comandos/encender-equipo/', {'equipo_id': equipo.id}, format='json')
        # No hay ESP32 'conectado' en este laboratorio todavía.
        self.assertEqual(r.status_code, 409)

    def test_hu20b_encender_equipo_encola_comando(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])

        equipo = self._equipo_con_relay(lab_id, ip='192.168.1.105', mac='AA:BB:CC:00:03:05')
        self.as_admin()
        r = self.client.post('/api/v1/control/comandos/encender-equipo/', {'equipo_id': equipo.id}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['estado'], 'pendiente')
        self.assertTrue(Comando.objects.filter(equipo=equipo, tipo_accion='encender_relay', estado='pendiente').exists())

    def test_hu20b_no_duplica_orden_pendiente(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])
        equipo = self._equipo_con_relay(lab_id, ip='192.168.1.106', mac='AA:BB:CC:00:03:06')

        self.as_admin()
        self.client.post('/api/v1/control/comandos/encender-equipo/', {'equipo_id': equipo.id}, format='json')
        r2 = self.client.post('/api/v1/control/comandos/encender-equipo/', {'equipo_id': equipo.id}, format='json')
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(Comando.objects.filter(equipo=equipo, tipo_accion='encender_relay').count(), 1)

    # ---------------- ESP32: pendientes + confirmar ----------------

    def test_esp32_confirma_encendido_actualiza_equipo(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id, identificador='ESP32-CONFIRMA')
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])
        equipo = self._equipo_con_relay(lab_id, ip='192.168.1.107', mac='AA:BB:CC:00:03:07')

        self.as_admin()
        self.client.post('/api/v1/control/comandos/encender-equipo/', {'equipo_id': equipo.id}, format='json')
        comando = Comando.objects.get(equipo=equipo, tipo_accion='encender_relay')

        # El ESP32 consulta pendientes con su API Key
        self.as_esp32()
        r = self.client.get(f'/api/v1/control/comandos/pendientes/?identificador=ESP32-CONFIRMA')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

        # El ESP32 confirma que lo ejecutó
        r2 = self.client.post(f'/api/v1/control/comandos/{comando.id}/confirmar/', {'exito': True}, format='json')
        self.assertEqual(r2.status_code, 200)

        equipo.refresh_from_db()
        self.assertEqual(equipo.estado_conexion, 'activo')

    # ---------------- HU-31 — Historial ----------------

    def test_hu31_historial_filtra_por_origen(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.108', mac='AA:BB:CC:00:03:08')
        equipo = Equipo.objects.get(id=eq_id)
        Comando.objects.create(equipo=equipo, tipo_accion='apagar_equipo', origen='manual', estado='ejecutado')
        Comando.objects.create(equipo=equipo, tipo_accion='apagar_equipo', origen='automatico', estado='ejecutado')

        self.as_admin()
        r = self.client.get('/api/v1/control/comandos/historial/?origen=manual')
        datos = r.data.get('results', r.data)
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]['origen'], 'manual')
