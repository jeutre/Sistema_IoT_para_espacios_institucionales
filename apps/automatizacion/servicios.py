"""
automatizacion/servicios.py

Motor de reglas que evalúa condiciones y ejecuta acciones automáticamente.
Se llama desde el endpoint manual /api/v1/automatizacion/evaluar/
y desde el scheduler (apps/automatizacion/scheduler.py).

CAMBIOS respecto a la versión anterior (Hallazgo crítico 1 y 2 del informe
de avance — HU-20B, HU-28, HU-29):

1. Antes SOLO se evaluaba la condición 'inactividad_minutos', sin importar
   qué decía regla.condicion. Esto hacía imposible que una regla de
   "encender_relay" o "encender_luces" se disparara por PRESENCIA (que es
   lo que pide HU-20B y HU-29): el motor únicamente sabía reaccionar a
   ausencia de movimiento. Ahora se evalúan las dos condiciones reales:
   'inactividad_minutos' (igual que antes) y la nueva 'ocupacion_detectada'.

2. Se respeta el horario configurado en la regla (HU-28: hora_inicio/hora_fin).

3. Se soporta accion_secundaria / valor_umbral_secundario para HU-28
   ("tiempo de espera antes de suspender" + "tiempo adicional antes del
   apagado total") sin necesitar dos reglas separadas.

4. Los comandos creados aquí (por el motor, no por un administrador) se
   marcan con origen='automatico', para que HU-32 pueda filtrarlos.
"""

from datetime import timedelta
from django.utils import timezone

from apps.automatizacion.models import ReglaAutomatizacion
from apps.dispositivos.models import Dispositivo
from apps.ocupacion.models import EventoOcupacion
from apps.equipos.models import Equipo
from apps.control.models import Comando
from apps.control.servicios import enviar_comando_a_equipo

ACCIONES_ESP32 = ('apagar_luces', 'encender_luces')
ACCIONES_PC = ('apagar_equipo', 'suspender_equipo')
ACCION_RELAY = 'encender_relay'


def evaluar_reglas() -> dict:
    """
    Evalúa todas las reglas activas (dentro de su horario, si tienen uno
    configurado) y ejecuta acciones si se cumplen sus condiciones.
    """
    reglas = ReglaAutomatizacion.objects.filter(activa=True)
    ahora = timezone.now()
    hora_local = timezone.localtime(ahora).time()

    resumen = {
        'reglas_evaluadas':  0,
        'reglas_omitidas_por_horario': 0,
        'comandos_esp32':    0,
        'comandos_pc':       0,
        'comandos_fallidos': 0,
    }

    for regla in reglas:
        resumen['reglas_evaluadas'] += 1

        if not regla.dentro_de_horario(hora_local):
            resumen['reglas_omitidas_por_horario'] += 1
            continue

        if regla.condicion == 'inactividad_minutos':
            _evaluar_inactividad(regla, ahora, resumen)
        elif regla.condicion == 'ocupacion_detectada':
            _evaluar_presencia(regla, ahora, resumen)

    return resumen


def _crear_comando_esp32_si_no_existe(disp, accion, equipo=None):
    """Anti-spam: no crear un comando si ya hay uno pendiente igual."""
    filtro = {'dispositivo': disp, 'tipo_accion': accion, 'estado': 'pendiente'}
    if equipo is not None:
        filtro['equipo'] = equipo
    if Comando.objects.filter(**filtro).exists():
        return False
    Comando.objects.create(dispositivo=disp, equipo=equipo, tipo_accion=accion, origen='automatico')
    return True


def _evaluar_inactividad(regla, ahora, resumen):
    """
    Condición 'inactividad_minutos': dispara accion_a_ejecutar cuando el
    último evento de ocupación de un dispositivo tiene más de
    regla.valor_umbral minutos. Si hay accion_secundaria configurada y ya
    pasaron valor_umbral_secundario minutos, también la dispara (HU-28:
    dos niveles, ej. suspender primero y apagar después).
    """
    umbral_tiempo = ahora - timedelta(minutes=regla.valor_umbral)
    accion = regla.accion_a_ejecutar

    umbral_secundario_tiempo = None
    if regla.accion_secundaria and regla.valor_umbral_secundario:
        umbral_secundario_tiempo = ahora - timedelta(minutes=regla.valor_umbral_secundario)

    # ── Comandos para ESP32 (luces, relay) ───────────────────────────────
    if accion in ACCIONES_ESP32 or (regla.accion_secundaria in ACCIONES_ESP32):
        for disp in Dispositivo.objects.filter(estado='conectado'):
            ultimo = EventoOcupacion.objects.filter(dispositivo=disp).order_by('-timestamp').first()
            if not ultimo:
                continue

            if accion in ACCIONES_ESP32 and ultimo.timestamp < umbral_tiempo:
                if _crear_comando_esp32_si_no_existe(disp, accion):
                    resumen['comandos_esp32'] += 1

            if (umbral_secundario_tiempo and regla.accion_secundaria in ACCIONES_ESP32
                    and ultimo.timestamp < umbral_secundario_tiempo):
                if _crear_comando_esp32_si_no_existe(disp, regla.accion_secundaria):
                    resumen['comandos_esp32'] += 1

    # ── Comandos para PCs (apagar, suspender) vía agente Windows ─────────
    if accion in ACCIONES_PC or (regla.accion_secundaria in ACCIONES_PC):
        for disp in Dispositivo.objects.filter(estado='conectado'):
            ultimo = EventoOcupacion.objects.filter(dispositivo=disp).order_by('-timestamp').first()
            if not ultimo:
                continue

            equipos = Equipo.objects.filter(
                laboratorio=disp.laboratorio, activo=True, estado_conexion='activo'
            )

            def _disparar_pc(nombre_accion):
                for equipo in equipos:
                    ya_existe = Comando.objects.filter(
                        equipo=equipo, tipo_accion=nombre_accion,
                        creado_en__gte=ahora - timedelta(minutes=5)
                    ).exists()
                    if ya_existe:
                        continue
                    cmd = enviar_comando_a_equipo(equipo, nombre_accion, origen='automatico')
                    if cmd.estado == 'ejecutado':
                        resumen['comandos_pc'] += 1
                    else:
                        resumen['comandos_fallidos'] += 1

            if accion in ACCIONES_PC and ultimo.timestamp < umbral_tiempo:
                _disparar_pc(accion)

            if (umbral_secundario_tiempo and regla.accion_secundaria in ACCIONES_PC
                    and ultimo.timestamp < umbral_secundario_tiempo):
                _disparar_pc(regla.accion_secundaria)


def _evaluar_presencia(regla, ahora, resumen):
    """
    Condición 'ocupacion_detectada' (Hallazgo crítico 1 — HU-20B, HU-29):
    dispara accion_a_ejecutar cuando el ÚLTIMO evento de ocupación de un
    dispositivo es 'ocupado' y ocurrió hace menos de regla.valor_umbral
    minutos (detección reciente). Pensada para 'encender_luces' y
    'encender_relay'.
    """
    accion = regla.accion_a_ejecutar
    if accion not in ('encender_luces', ACCION_RELAY):
        return

    limite_reciente = ahora - timedelta(minutes=regla.valor_umbral)

    for disp in Dispositivo.objects.filter(estado='conectado'):
        ultimo = EventoOcupacion.objects.filter(dispositivo=disp).order_by('-timestamp').first()
        if not ultimo or ultimo.estado != 'ocupado' or ultimo.timestamp < limite_reciente:
            continue

        if accion == 'encender_luces':
            if _crear_comando_esp32_si_no_existe(disp, 'encender_luces'):
                resumen['comandos_esp32'] += 1

        elif accion == ACCION_RELAY:
            # Solo tiene sentido "encender" equipos que hoy están inactivos
            # y que físicamente tienen un relay configurado (HU-13B/HU-20B).
            equipos = Equipo.objects.filter(
                laboratorio=disp.laboratorio, activo=True,
                estado_conexion='inactivo', tiene_relay=True,
            )
            for equipo in equipos:
                if _crear_comando_esp32_si_no_existe(disp, ACCION_RELAY, equipo=equipo):
                    resumen['comandos_esp32'] += 1
