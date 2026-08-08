"""
Aceptación — ÉPICA 2: Gestión de laboratorios.
HU-03 Registrar · HU-04 Actualizar · HU-05 Visualizar.
"""
from apps.acceptance_base import AcceptanceBase


class LaboratorioTests(AcceptanceBase):

    # ---------------- HU-03 — Registrar ----------------

    def test_hu03_registrar_laboratorio(self):
        self.as_admin()
        r = self.client.post('/api/v1/laboratorio/', {
            'nombre': 'Lab Redes', 'ubicacion': 'Bloque B', 'capacidad': 25,
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['nombre'], 'Lab Redes')
        self.assertEqual(r.data['capacidad'], 25)

    def test_hu03_registrar_requiere_admin(self):
        self.as_no_admin()
        r = self.client.post('/api/v1/laboratorio/', {
            'nombre': 'X', 'ubicacion': 'Y', 'capacidad': 1,
        }, format='json')
        self.assertEqual(r.status_code, 403)

    # ---------------- HU-04 — Actualizar ----------------

    def test_hu04_actualizar_laboratorio(self):
        lab_id = self.crear_laboratorio(nombre='Lab Viejo', capacidad=10)
        self.as_admin()
        r = self.client.patch(f'/api/v1/laboratorio/{lab_id}/', {
            'nombre': 'Lab Nuevo', 'capacidad': 40,
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['nombre'], 'Lab Nuevo')
        self.assertEqual(r.data['capacidad'], 40)

    # ---------------- HU-05 — Visualizar ----------------

    def test_hu05_visualizar_lista(self):
        self.crear_laboratorio(nombre='Lab 1')
        self.crear_laboratorio(nombre='Lab 2')
        self.as_admin()
        r = self.client.get('/api/v1/laboratorio/')
        self.assertEqual(r.status_code, 200)
        nombres = [x['nombre'] for x in (r.data.get('results', r.data))]
        self.assertIn('Lab 1', nombres)
        self.assertIn('Lab 2', nombres)

    def test_hu05_visualizar_detalle(self):
        lab_id = self.crear_laboratorio(nombre='Lab Detalle')
        self.as_admin()
        r = self.client.get(f'/api/v1/laboratorio/{lab_id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['nombre'], 'Lab Detalle')