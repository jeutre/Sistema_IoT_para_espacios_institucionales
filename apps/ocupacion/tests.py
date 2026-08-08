"""
Aceptación — ÉPICA 4: Ocupación (sensor PIR).
HU-09 Recibir datos PIR · HU-10 Tiempo real · HU-11 Historial · HU-12 Horas pico.

Todos los eventos de ocupación se generan con el JSON EXACTO del firmware
(dispositivo_id + estado, cabecera Api-Key), no insertando filas a mano.
"""
from django.utils import timezone
from datetime import timedelta
from apps.acceptance_base import AcceptanceBase


class OcupacionTests(AcceptanceBase):

    def _setup_lab_esp32(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        return lab_id, disp_id

    # ---------------- HU-09 — Recibir datos del PIR ----------------

    def test_hu09_pir_ocupado(self):
        _, disp_id = self._setup_lab_esp32()
        r = self.esp32_reporta_pir(disp_id, 'ocupado')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['estado'], 'ocupado')

    def test_hu09_pir_vacio(self):
        _, disp_id = self._setup_lab_esp32()
        r = self.esp32_reporta_pir(disp_id, 'vacio')
        self.assertEqual(r.status_code, 201)

    def test_hu09_pir_estado_invalido_rechazado(self):
        # El firmware solo manda ocupado/vacio; cualquier otra cosa es basura.
        _, disp_id = self._setup_lab_esp32()
        r = self.esp32_reporta_pir(disp_id, 'PLATANO')
        self.assertEqual(r.status_code, 400)

    def test_hu09_pir_sin_api_key_rechazado(self):
        _, disp_id = self._setup_lab_esp32()
        self.as_anon()
        r = self.client.post('/api/v1/ocupacion/pir/', {
            'dispositivo_id': disp_id, 'estado': 'ocupado',
        }, format='json')
        self.assertIn(r.status_code, (401, 403))

    # ---------------- HU-10 — Ocupación en tiempo real ----------------

    def test_hu10_tiempo_real_refleja_ultimo_estado(self):
        _, disp_id = self._setup_lab_esp32()
        self.esp32_reporta_pir(disp_id, 'ocupado')
        self.as_admin()
        r = self.client.get('/api/v1/ocupacion/tiempo-real/')
        self.assertEqual(r.status_code, 200)
        estados = {x['dispositivo']: x['estado'] for x in r.data}
        self.assertEqual(estados.get('ESP32-01'), 'ocupado')

    def test_hu10_tiempo_real_cambia_a_vacio(self):
        _, disp_id = self._setup_lab_esp32()
        self.esp32_reporta_pir(disp_id, 'ocupado')
        self.esp32_reporta_pir(disp_id, 'vacio')
        self.as_admin()
        r = self.client.get('/api/v1/ocupacion/tiempo-real/')
        estados = {x['dispositivo']: x['estado'] for x in r.data}
        self.assertEqual(estados.get('ESP32-01'), 'vacio')

    # ---------------- HU-11 — Historial de ocupación ----------------

    def test_hu11_historial_filtra_por_fecha(self):
        _, disp_id = self._setup_lab_esp32()
        self.esp32_reporta_pir(disp_id, 'ocupado')
        self.esp32_reporta_pir(disp_id, 'vacio')
        hoy = timezone.localdate().isoformat()
        self.as_admin()
        r = self.client.get(f'/api/v1/ocupacion/?desde={hoy}&hasta={hoy}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 2)

    def test_hu11_historial_rango_pasado_vacio(self):
        _, disp_id = self._setup_lab_esp32()
        self.esp32_reporta_pir(disp_id, 'ocupado')
        ayer = (timezone.localdate() - timedelta(days=1)).isoformat()
        self.as_admin()
        r = self.client.get(f'/api/v1/ocupacion/?desde={ayer}&hasta={ayer}')
        self.assertEqual(r.data['count'], 0)

    def test_hu11_historial_filtra_por_dispositivo(self):
        _, disp_id = self._setup_lab_esp32()
        self.esp32_reporta_pir(disp_id, 'ocupado')
        self.as_admin()
        r = self.client.get(f'/api/v1/ocupacion/?dispositivo={disp_id}')
        self.assertEqual(r.data['count'], 1)

    # ---------------- HU-12 — Horas pico ----------------

    def test_hu12_horas_pico_cuenta_ocupados(self):
        _, disp_id = self._setup_lab_esp32()
        # 3 reportes "ocupado" reales enviados por el ESP32.
        for _ in range(3):
            self.esp32_reporta_pir(disp_id, 'ocupado')
        self.esp32_reporta_pir(disp_id, 'vacio')  # este NO cuenta como pico
        self.as_admin()
        r = self.client.get('/api/v1/ocupacion/horas-pico/')
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(r.data['hora_pico'])
        total = sum(h['total_eventos_ocupado'] for h in r.data['detalle_por_hora'])
        self.assertEqual(total, 3)   # solo los 'ocupado'