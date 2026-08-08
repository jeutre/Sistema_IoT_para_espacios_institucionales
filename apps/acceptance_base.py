"""
apps/acceptance_base.py

Clase base para las pruebas de aceptación de todas las épicas.
Provee un cliente DRF y helpers de autenticación y de alta de entidades,
para que cada test ejerza los endpoints REALES (no filas insertadas a mano).

NOTA: este archivo faltaba en el repositorio; sin él, TODA la suite de tests
fallaba al importar. Se reconstruyó a partir del uso que hacen los tests.
"""
from rest_framework.test import APITestCase
from rest_framework_api_key.models import APIKey
from django.contrib.auth import get_user_model

User = get_user_model()


class AcceptanceBase(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_test', email='admin@test.local', password='clave12345')
        self.usuario = User.objects.create_user(
            username='user_test', email='user@test.local', password='clave12345')
        # API Key que representa al ESP32 (autenticación de dispositivo, no JWT).
        _, self.api_key = APIKey.objects.create_key(name='esp32-test')

    # ── Cambios de identidad ────────────────────────────────────────────────
    def as_admin(self):
        self.client.credentials()
        self.client.force_authenticate(user=self.admin)

    def as_no_admin(self):
        self.client.credentials()
        self.client.force_authenticate(user=self.usuario)

    def as_esp32(self):
        self.client.force_authenticate(user=None)
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.api_key}')

    def as_anon(self):
        self.client.force_authenticate(user=None)
        self.client.credentials()

    # ── Altas por los endpoints reales ──────────────────────────────────────
    def crear_laboratorio(self, nombre='Lab Test', ubicacion='Bloque X', capacidad=30):
        self.as_admin()
        r = self.client.post('/api/v1/laboratorio/', {
            'nombre': nombre, 'ubicacion': ubicacion, 'capacidad': capacidad,
        }, format='json')
        assert r.status_code == 201, f'crear_laboratorio falló: {r.status_code} {r.data}'
        return r.data['id']

    def registrar_esp32(self, lab_id, identificador='ESP32-01',
                        ip='192.168.1.60', mac_address='24:6F:28:00:00:01'):
        self.as_admin()
        r = self.client.post('/api/v1/dispositivos/esp32/', {
            'laboratorio': lab_id, 'identificador': identificador,
            'ip': ip, 'mac_address': mac_address,
        }, format='json')
        assert r.status_code == 201, f'registrar_esp32 falló: {r.status_code} {r.data}'
        return r.data['id']

    def registrar_equipo(self, lab_id, nombre='PC-Test',
                         ip='192.168.1.50', mac='AA:BB:CC:00:00:99'):
        self.as_admin()
        r = self.client.post('/api/v1/equipos/', {
            'laboratorio': lab_id, 'nombre': nombre, 'ip': ip, 'mac': mac,
        }, format='json')
        assert r.status_code == 201, f'registrar_equipo falló: {r.status_code} {r.data}'
        return r.data['id']

    def esp32_reporta_pir(self, disp_id, estado):
        """El ESP32 reporta ocupación por el endpoint real, con su API Key."""
        self.as_esp32()
        return self.client.post('/api/v1/ocupacion/pir/', {
            'dispositivo_id': disp_id, 'estado': estado,
        }, format='json')