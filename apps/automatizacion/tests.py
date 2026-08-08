"""
Aceptación — ÉPICA 8: Automatización energética.
HU-28 Configurar reglas · HU-29 Encendido automático de iluminación ·
HU-30 Apagado automático de iluminación · HU-31/HU-32 Historial.

Este archivo estaba vacío en el repositorio original. Se agregan pruebas
reales, incluyendo las que cubren el Hallazgo crítico 1 del informe de
avance (el motor de reglas no podía disparar acciones por presencia).
"""
from datetime import time, timedelta
from unittest.mock import patch
from django.utils import timezone
from apps.acceptance_base import AcceptanceBase
from apps.automatizacion.models import ReglaAutomatizacion
from apps.automatizacion.servicios import evaluar_reglas
from apps.control.models import Comando
from apps.equipos.models import Equipo


class AutomatizacionTests(AcceptanceBase):

    def _crear_regla(self, **kwargs):
        defaults = dict(
            nombre='Regla de prueba',
            condicion='inactividad_minutos',
            valor_umbral=15,
            accion_a_ejecutar='apagar_luces',
            activa=True,
        )
        defaults.update(kwargs)
        return ReglaAutomatizacion.objects.create(**defaults)

    # ---------------- HU-28 — CRUD de reglas ----------------

    def test_hu28_crear_regla_via_api(self):
        self.as_admin()
        r = self.client.post('/api/v1/automatizacion/reglas/', {
            'nombre': 'Apagar luces por inactividad',
            'condicion': 'inactividad_minutos',
            'valor_umbral': 20,
            'accion_a_ejecutar': 'apagar_luces',
            'activa': True,
        }, format='json')
        self.assertEqual(r.status_code, 201)

    def test_hu28_regla_con_horario_y_accion_secundaria(self):
        self.as_admin()
        r = self.client.post('/api/v1/automatizacion/reglas/', {
            'nombre': 'Suspender y luego apagar',
            'condicion': 'inactividad_minutos',
            'valor_umbral': 15,
            'accion_a_ejecutar': 'suspender_equipo',
            'valor_umbral_secundario': 45,
            'accion_secundaria': 'apagar_equipo',
            'hora_inicio': '06:00:00',
            'hora_fin': '22:00:00',
            'activa': True,
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['accion_secundaria'], 'apagar_equipo')

    # ---------------- HU-30 — Apagado automático (caso ya correcto) ----------

    def test_hu30_apaga_luces_tras_inactividad(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        # Evento de ocupación "viejo" (más de 15 min) -> debe disparar apagar_luces
        r = self.esp32_reporta_pir(disp_id, 'ocupado')
        self.assertEqual(r.status_code, 201)
        from apps.dispositivos.models import Dispositivo
        from apps.ocupacion.models import EventoOcupacion
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])
        EventoOcupacion.objects.filter(dispositivo=disp).update(
            timestamp=timezone.now() - timedelta(minutes=20)
        )

        self._crear_regla(condicion='inactividad_minutos', valor_umbral=15, accion_a_ejecutar='apagar_luces')
        resumen = evaluar_reglas()
        self.assertEqual(resumen['comandos_esp32'], 1)
        self.assertTrue(Comando.objects.filter(dispositivo=disp, tipo_accion='apagar_luces', origen='automatico').exists())

    # ---------------- Hallazgo crítico 1 — HU-29 encendido por presencia -----

    def test_hu29_enciende_luces_por_presencia_reciente(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])

        # Presencia detectada AHORA MISMO (evento reciente).
        r = self.esp32_reporta_pir(disp_id, 'ocupado')
        self.assertEqual(r.status_code, 201)

        self._crear_regla(condicion='ocupacion_detectada', valor_umbral=5, accion_a_ejecutar='encender_luces')
        resumen = evaluar_reglas()
        self.assertEqual(resumen['comandos_esp32'], 1)
        self.assertTrue(Comando.objects.filter(dispositivo=disp, tipo_accion='encender_luces', origen='automatico').exists())

    def test_hu29_no_enciende_si_la_presencia_es_antigua(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.dispositivos.models import Dispositivo
        from apps.ocupacion.models import EventoOcupacion
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])
        self.esp32_reporta_pir(disp_id, 'ocupado')
        # El evento "ocupado" ya tiene 30 minutos -> no es una detección reciente.
        EventoOcupacion.objects.filter(dispositivo=disp).update(
            timestamp=timezone.now() - timedelta(minutes=30)
        )

        self._crear_regla(condicion='ocupacion_detectada', valor_umbral=5, accion_a_ejecutar='encender_luces')
        resumen = evaluar_reglas()
        self.assertEqual(resumen['comandos_esp32'], 0)

    def test_hu20b_encender_relay_por_presencia_solo_equipos_inactivos(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])

        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.90', mac='AA:BB:CC:00:02:00')
        equipo = Equipo.objects.get(id=eq_id)
        equipo.tiene_relay = True
        equipo.relay_gpio = 4
        equipo.estado_conexion = 'inactivo'
        equipo.save(update_fields=['tiene_relay', 'relay_gpio', 'estado_conexion'])

        self.esp32_reporta_pir(disp_id, 'ocupado')  # presencia reciente

        self._crear_regla(condicion='ocupacion_detectada', valor_umbral=5, accion_a_ejecutar='encender_relay')
        resumen = evaluar_reglas()
        self.assertEqual(resumen['comandos_esp32'], 1)
        self.assertTrue(Comando.objects.filter(equipo=equipo, tipo_accion='encender_relay', origen='automatico').exists())

    def test_hu20b_no_reencender_equipo_ya_activo(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.dispositivos.models import Dispositivo
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])

        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.91', mac='AA:BB:CC:00:02:01')
        equipo = Equipo.objects.get(id=eq_id)
        equipo.tiene_relay = True
        equipo.relay_gpio = 5
        equipo.estado_conexion = 'activo'  # ya está encendido
        equipo.save(update_fields=['tiene_relay', 'relay_gpio', 'estado_conexion'])

        self.esp32_reporta_pir(disp_id, 'ocupado')
        self._crear_regla(condicion='ocupacion_detectada', valor_umbral=5, accion_a_ejecutar='encender_relay')
        resumen = evaluar_reglas()
        self.assertEqual(resumen['comandos_esp32'], 0)

    # ---------------- HU-28 — Horario institucional ----------------

    def test_hu28_regla_fuera_de_horario_se_omite(self):
        lab_id = self.crear_laboratorio()
        disp_id = self.registrar_esp32(lab_id)
        from apps.dispositivos.models import Dispositivo
        from apps.ocupacion.models import EventoOcupacion
        disp = Dispositivo.objects.get(id=disp_id)
        disp.estado = 'conectado'
        disp.save(update_fields=['estado'])
        self.esp32_reporta_pir(disp_id, 'ocupado')
        EventoOcupacion.objects.filter(dispositivo=disp).update(
            timestamp=timezone.now() - timedelta(minutes=20)
        )

        # Ventana horaria que, con seguridad, NO incluye la hora actual:
        # una franja de 1 minuto de duración a la hora exactamente opuesta.
        ahora_local = timezone.localtime(timezone.now())
        opuesta = (ahora_local.hour + 12) % 24
        self._crear_regla(
            condicion='inactividad_minutos', valor_umbral=15, accion_a_ejecutar='apagar_luces',
            hora_inicio=time(opuesta, 0), hora_fin=time(opuesta, 1),
        )
        resumen = evaluar_reglas()
        self.assertEqual(resumen['comandos_esp32'], 0)
        self.assertEqual(resumen['reglas_omitidas_por_horario'], 1)

    # ---------------- HU-32 — Historial de automatizaciones ----------------

    def test_hu32_historial_solo_muestra_comandos_automaticos(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.92', mac='AA:BB:CC:00:02:02')
        equipo = Equipo.objects.get(id=eq_id)

        Comando.objects.create(equipo=equipo, tipo_accion='apagar_equipo', origen='manual', estado='ejecutado')
        Comando.objects.create(equipo=equipo, tipo_accion='apagar_equipo', origen='automatico', estado='ejecutado')

        self.as_admin()
        r = self.client.get('/api/v1/automatizacion/historial/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['origen'], 'automatico')

    def test_hu31_historial_de_control_muestra_todos(self):
        lab_id = self.crear_laboratorio()
        eq_id = self.registrar_equipo(lab_id, ip='192.168.1.93', mac='AA:BB:CC:00:02:03')
        equipo = Equipo.objects.get(id=eq_id)
        Comando.objects.create(equipo=equipo, tipo_accion='apagar_equipo', origen='manual', estado='ejecutado')
        Comando.objects.create(equipo=equipo, tipo_accion='apagar_equipo', origen='automatico', estado='ejecutado')

        self.as_admin()
        r = self.client.get('/api/v1/control/comandos/historial/')
        self.assertEqual(r.status_code, 200)
        datos = r.data.get('results', r.data)
        self.assertEqual(len(datos), 2)
