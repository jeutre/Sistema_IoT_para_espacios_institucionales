"""
Aceptación — ÉPICA 7: Alertas.
HU-24 Fuera de horario · HU-25 Desconexión ESP32 · HU-26 Equipo sin
ocupación · HU-27 Historial de alertas.

Este archivo estaba vacío en el repositorio original.

Nota: HU-25 y HU-26 se generan desde el scheduler (tareas en segundo
plano), no desde una petición HTTP síncrona, así que se prueban llamando
directamente a las funciones de apps/automatizacion/scheduler.py — igual
que tendría que hacerlo cualquier test de una tarea periódica.
"""
from datetime import timedelta
from django.utils import timezone
from apps.acceptance_base import AcceptanceBase
from apps.alertas.models import Alerta


class AlertasTests(AcceptanceBase):

    def test_alertas_requiere_admin(self):
        self.as_no_admin()
        r = self.client.get('/api/v1/alertas/')
        self.assertIn(r.status_code, (403, 401))

    # ---------------- HU-24 — Movimiento fuera de horario ----------------

    def test_hu24_genera_alerta_fuera_de_horario(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)

        from apps.ocupacion.models import EventoOcupacion
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)

        # Se fuerza directamente un evento a las 03:00 (fuera de horario
        # institucional 06:00-22:00) para no depender de la hora real en
        # que corre el test.
        hora_madrugada = timezone.now().replace(hour=3, minute=0, second=0, microsecond=0)
        EventoOcupacion.objects.create(dispositivo=disp, estado='ocupado', timestamp=hora_madrugada)

        self.assertTrue(Alerta.objects.filter(tipo='movimiento').exists())

    def test_hu24_no_genera_alerta_dentro_de_horario(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.ocupacion.models import EventoOcupacion
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)

        hora_habil = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        EventoOcupacion.objects.create(dispositivo=disp, estado='ocupado', timestamp=hora_habil)

        self.assertFalse(Alerta.objects.filter(tipo='movimiento', object_id=disp.id).exists())

    # ---------------- Alerta de desconexión de EQUIPO (PC) ----------------

    def test_alerta_desconexion_de_equipo(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.130', mac='AA:BB:CC:00:06:00')
        from apps.equipos.models import EventoConexion, Equipo
        equipo = Equipo.objects.get(id=eq_id)
        EventoConexion.objects.create(equipo=equipo, tipo='desconexion')

        self.assertTrue(Alerta.objects.filter(tipo='desconexion', object_id=equipo.id).exists())

    # ---------------- HU-25 — Desconexión de ESP32 (scheduler) ----------------

    def test_hu25_marca_esp32_desconectado_y_alerta(self):
        from apps.automatizacion.scheduler import _tarea_marcar_esp32_desconectados
        from apps.dispositivos.models import Dispositivo

        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.ultima_conexion = timezone.now() - timedelta(minutes=10)  # más del timeout
        disp.save(update_fields=['estado', 'ultima_conexion'])

        _tarea_marcar_esp32_desconectados()

        disp.refresh_from_db()
        self.assertEqual(disp.estado, 'desconectado')
        self.assertTrue(Alerta.objects.filter(tipo='desconexion', object_id=disp.id).exists())

    def test_hu25_no_duplica_alerta_si_ya_esta_desconectado_y_alertado(self):
        from apps.automatizacion.scheduler import _tarea_marcar_esp32_desconectados
        from apps.dispositivos.models import Dispositivo

        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.ultima_conexion = timezone.now() - timedelta(minutes=10)
        disp.save(update_fields=['estado', 'ultima_conexion'])

        _tarea_marcar_esp32_desconectados()
        _tarea_marcar_esp32_desconectados()  # segunda corrida del scheduler

        total = Alerta.objects.filter(tipo='desconexion', object_id=disp.id).count()
        self.assertEqual(total, 1)

    # ---------------- HU-26 — Equipo activo sin ocupación (scheduler) ------

    def test_hu26_alerta_equipo_encendido_en_laboratorio_vacio(self):
        from apps.automatizacion.scheduler import _tarea_alerta_equipo_sin_ocupacion
        from apps.equipos.models import Equipo

        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.131', mac='AA:BB:CC:00:06:01')
        Equipo.objects.filter(id=eq_id).update(estado_conexion='activo')
        # No se reporta ningún evento PIR -> el laboratorio se considera vacío.

        _tarea_alerta_equipo_sin_ocupacion()

        self.assertTrue(Alerta.objects.filter(tipo='equipo_sin_ocupacion').exists())

    def test_hu26_no_alerta_si_laboratorio_esta_ocupado(self):
        from apps.automatizacion.scheduler import _tarea_alerta_equipo_sin_ocupacion

        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.132', mac='AA:BB:CC:00:06:02')
        from apps.equipos.models import Equipo
        Equipo.objects.filter(id=eq_id).update(estado_conexion='activo')
        self.esp32_reporta_pir(disp_id, 'ocupado')  # laboratorio ocupado

        _tarea_alerta_equipo_sin_ocupacion()

        from django.contrib.contenttypes.models import ContentType
        from apps.laboratorio.models import Laboratorio
        ctype = ContentType.objects.get_for_model(Laboratorio)
        self.assertFalse(Alerta.objects.filter(tipo='equipo_sin_ocupacion', content_type=ctype, object_id=lab_id).exists())

    # ---------------- HU-27 — Historial de alertas ----------------

    def test_hu27_historial_filtra_por_tipo(self):
        Alerta.objects.create(tipo='movimiento', descripcion='a', nivel='critico')
        Alerta.objects.create(tipo='desconexion', descripcion='b', nivel='critico')

        self.as_admin()
        r = self.client.get('/api/v1/alertas/?tipo=movimiento')
        datos = r.data.get('results', r.data)
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]['tipo'], 'movimiento')

    def test_hu27_marcar_alerta_como_leida(self):
        alerta = Alerta.objects.create(tipo='movimiento', descripcion='c', nivel='medio')
        self.as_admin()
        r = self.client.patch(f'/api/v1/alertas/{alerta.id}/', {'leida': True}, format='json')
        self.assertEqual(r.status_code, 200)
        alerta.refresh_from_db()
        self.assertTrue(alerta.leida)
