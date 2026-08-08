"""
Aceptación — ÉPICA 3: Dispositivos ESP32.
HU-06 Registrar ESP32 · HU-07 Estado de conexión · HU-08 Historial de comunicación.

Nota sobre el ping (HU-07): el resultado físico de un ping depende de que el
ESP32 esté encendido y en la red. En una prueba automática no hay un ESP32 al
que apagar/encender, así que sustituimos SOLO la función de ping por un doble
que representa "ESP32 responde" / "ESP32 no responde". El endpoint, la ruta y la
respuesta son los reales; lo único simulado es el estado físico del aparato.
"""
from unittest.mock import patch
from apps.acceptance_base import AcceptanceBase


class DispositivoTests(AcceptanceBase):

    # ---------------- HU-06 — Registrar ESP32 ----------------

    def test_hu06_registrar_esp32(self):
        lab_id = self.crear_laboratorio()
        self.as_admin()
        r = self.client.post('/api/v1/dispositivos/esp32/', {
            'laboratorio': lab_id, 'identificador': 'ESP32-AULA-5',
            'ip': '192.168.1.61', 'mac_address': '24:6F:28:AA:BB:05',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['identificador'], 'ESP32-AULA-5')

    def test_hu06_registrar_requiere_admin(self):
        lab_id = self.crear_laboratorio()
        self.as_no_admin()
        r = self.client.post('/api/v1/dispositivos/esp32/', {
            'laboratorio': lab_id, 'identificador': 'X', 'ip': '192.168.1.62',
        }, format='json')
        self.assertEqual(r.status_code, 403)

    # ---------------- HU-07 — Estado de conexión ----------------

    @patch('apps.dispositivos.views.ejecutar_ping', return_value=(True, None))
    def test_hu07_esp32_encendido_queda_conectado(self, _mock):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        self.as_admin()
        r = self.client.get(f'/api/v1/dispositivos/esp32/{disp_id}/ping/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['estado'], 'conectado')
        self.assertTrue(r.data['conectado'])

    @patch('apps.dispositivos.views.ejecutar_ping', return_value=(False, None))
    def test_hu07_esp32_apagado_devuelve_200_no_500(self, _mock):
        # Regresión del bug: un ESP32 apagado NO debe romper la vista.
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        self.as_admin()
        r = self.client.get(f'/api/v1/dispositivos/esp32/{disp_id}/ping/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['estado'], 'desconectado')
        self.assertFalse(r.data['conectado'])

    # ---------------- HU-08 — Historial de comunicación ----------------

    def test_hu08_esp32_reporta_y_queda_en_historial(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        # El ESP32 envía un mensaje con su API Key (no JWT).
        self.as_esp32()
        r = self.client.post('/api/v1/dispositivos/historial/recibir/', {
            'dispositivo_id': disp_id, 'mensaje': 'heartbeat',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        # El admin puede consultar el historial filtrado por dispositivo.
        self.as_admin()
        r = self.client.get(f'/api/v1/dispositivos/historial/?dispositivo={disp_id}')
        self.assertEqual(r.status_code, 200)
        datos = r.data.get('results', r.data)
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]['mensaje'], 'heartbeat')

    def test_hu08_recibir_sin_api_key_rechazado(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        self.as_anon()
        r = self.client.post('/api/v1/dispositivos/historial/recibir/', {
            'dispositivo_id': disp_id, 'mensaje': 'x',
        }, format='json')
        self.assertIn(r.status_code, (401, 403))