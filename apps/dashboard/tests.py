"""
Aceptación — ÉPICA 6: Dashboard y KPIs.
HU-21 Dashboard general · HU-23 KPIs institucionales.

Este archivo estaba vacío en el repositorio original
(solo tenía "# Create your tests here.").
"""
from datetime import timedelta
from django.utils import timezone
from apps.acceptance_base import AcceptanceBase
from apps.equipos.models import Equipo


class DashboardTests(AcceptanceBase):

    def test_dashboard_requiere_admin(self):
        self.as_no_admin()
        r = self.client.get('/api/v1/dashboard/resumen/')
        self.assertIn(r.status_code, (403, 401))

    def test_dashboard_anonimo_rechazado(self):
        self.as_anon()
        r = self.client.get('/api/v1/dashboard/resumen/')
        self.assertIn(r.status_code, (403, 401))

    # ---------------- HU-21 — Dashboard general ----------------

    def test_hu21_resumen_estructura_basica(self):
        self.crear_laboratorio()
        self.as_admin()
        r = self.client.get('/api/v1/dashboard/resumen/')
        self.assertEqual(r.status_code, 200)
        for clave in ('laboratorios', 'equipos', 'dispositivos'):
            self.assertIn(clave, r.data)

    def test_hu21_cuenta_laboratorios_activos(self):
        self.crear_laboratorio()
        self.crear_laboratorio()
        self.as_admin()
        r = self.client.get('/api/v1/dashboard/resumen/')
        self.assertGreaterEqual(r.data['laboratorios']['totales'], 2)

    def test_hu21_ocupacion_actual_refleja_evento_reciente(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        self.esp32_reporta_pir(disp_id, 'ocupado')
        self.as_admin()
        r = self.client.get('/api/v1/dashboard/resumen/')
        self.assertGreaterEqual(r.data['laboratorios']['ocupados_actualmente'], 1)

    # ---------------- HU-23 — KPIs institucionales ----------------

    def test_hu23_kpis_estructura_basica(self):
        self.as_admin()
        r = self.client.get('/api/v1/dashboard/kpis/')
        self.assertEqual(r.status_code, 200)
        for clave in ('porcentaje_ocupacion', 'disponibilidad_equipos',
                      'tiempo_promedio_inactividad_min', 'ahorro_energetico',
                      'eficiencia_operativa'):
            self.assertIn(clave, r.data)

    def test_hu23_kpis_respeta_filtro_de_fechas(self):
        self.as_admin()
        ayer = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.get(f'/api/v1/dashboard/kpis/?desde={ayer}&hasta={ayer}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['porcentaje_ocupacion'], 0.0)

    def test_hu23_disponibilidad_equipos_con_datos(self):
        lab_id = self.crear_laboratorio()
        eq1 = self.registrar_equipo(lab_id, nombre='PC-A', ip='192.168.1.120', mac='AA:BB:CC:00:05:00')
        eq2 = self.registrar_equipo(lab_id, nombre='PC-B', ip='192.168.1.121', mac='AA:BB:CC:00:05:01')
        Equipo.objects.filter(id=eq1).update(estado_conexion='activo')
        Equipo.objects.filter(id=eq2).update(estado_conexion='inactivo')

        self.as_admin()
        r = self.client.get('/api/v1/dashboard/kpis/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['disponibilidad_equipos'], 50.0)

    def test_hu23_ahorro_energetico_incluye_equipos_inactivos(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.122', mac='AA:BB:CC:00:05:02')
        equipo = Equipo.objects.get(id=eq_id)
        equipo.estado_conexion = 'inactivo'
        equipo.ultima_actividad = timezone.now() - timedelta(hours=1)
        equipo.save(update_fields=['estado_conexion', 'ultima_actividad'])

        self.as_admin()
        r = self.client.get('/api/v1/dashboard/kpis/')
        self.assertGreater(r.data['ahorro_energetico']['ahorro_potencial_wh'], 0)
