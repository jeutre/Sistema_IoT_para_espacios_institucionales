"""
apps/automatizacion/scheduler.py

Scheduler de fondo (APScheduler) que corre dentro del proceso Django.
Tareas periódicas:
  1. Evaluación de reglas de automatización.
  2. Ping automático a equipos IPv4 (HU-14).
  3. Auto-desconexión de ESP32 sin heartbeat + alerta (HU-07 / HU-25).
  4. Alerta de equipo activo sin ocupación (HU-26).
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from datetime import datetime

log = logging.getLogger(__name__)

# Intervalo de evaluación de reglas (por defecto 5 min).
INTERVALO_MINUTOS = getattr(settings, 'AUTOMATIZACION_INTERVALO_MINUTOS', 5)

# Intervalo del ping automático a equipos (por defecto 2 min). (HU-14)
PING_INTERVALO_MINUTOS = getattr(settings, 'PING_INTERVALO_MINUTOS', 2)

# Auto-desconexión de ESP32 (HU-07/HU-25)
ESP32_TIMEOUT_MINUTOS = getattr(settings, 'ESP32_TIMEOUT_MINUTOS', 3)
ESP32_CHECK_INTERVALO_MINUTOS = getattr(settings, 'ESP32_CHECK_INTERVALO_MINUTOS', 1)

_scheduler = None


def _tarea_evaluar_reglas():
    try:
        from .servicios import evaluar_reglas
        resumen = evaluar_reglas()
        log.info(
            f"[Scheduler] Evaluación completada — "
            f"Reglas: {resumen['reglas_evaluadas']} | "
            f"Comandos ESP32: {resumen['comandos_esp32']} | "
            f"Comandos PC: {resumen['comandos_pc']} | "
            f"Fallidos: {resumen['comandos_fallidos']}"
        )
    except Exception as e:
        log.error(f"[Scheduler] Error en evaluación de reglas: {e}", exc_info=True)


def _tarea_ping_equipos():
    try:
        from concurrent.futures import ThreadPoolExecutor
        from apps.equipos.models import Equipo
        from apps.equipos.views import ejecutar_ping, actualizar_estado_equipo

        equipos = list(Equipo.objects.filter(activo=True))
        if not equipos:
            log.info("[Scheduler] Ping automático — no hay equipos registrados.")
            return

        with ThreadPoolExecutor(max_workers=20) as executor:
            respuestas = list(executor.map(lambda e: ejecutar_ping(e.ip), equipos))

        activos = 0
        cambios = 0
        for equipo, responde in zip(equipos, respuestas):
            if actualizar_estado_equipo(equipo, responde):
                cambios += 1
            if responde:
                activos += 1

        log.info(
            f"[Scheduler] Ping automático — Equipos: {len(equipos)} | "
            f"Activos: {activos} | Inactivos: {len(equipos) - activos} | "
            f"Cambios de estado: {cambios}"
        )
    except Exception as e:
        log.error(f"[Scheduler] Error en ping automático: {e}", exc_info=True)


def _tarea_marcar_esp32_desconectados():
    """HU-25 — Marca ESP32 sin comunicación reciente como 'desconectado'."""
    try:
        from datetime import timedelta
        from django.db.models import Q
        from django.utils import timezone
        from django.contrib.contenttypes.models import ContentType
        from apps.dispositivos.models import Dispositivo
        from apps.alertas.models import Alerta

        ahora = timezone.now()
        limite = ahora - timedelta(minutes=ESP32_TIMEOUT_MINUTOS)
        obsoletos = list(Dispositivo.objects.filter(estado='conectado').filter(
            Q(ultima_conexion__lt=limite) | Q(ultima_conexion__isnull=True)
        ))
        if not obsoletos:
            return

        ctype = ContentType.objects.get_for_model(Dispositivo)
        for disp in obsoletos:
            disp.estado = 'desconectado'
            disp.save(update_fields=['estado'])

            ya_alertado = Alerta.objects.filter(
                tipo='desconexion', object_id=disp.id,
                content_type=ctype, leida=False
            ).exists()
            if ya_alertado:
                continue

            if disp.ultima_conexion:
                mins = int((ahora - disp.ultima_conexion).total_seconds() // 60)
                detalle = f'Lleva {mins} min sin comunicarse.'
            else:
                detalle = 'Nunca ha comunicado.'
            Alerta.objects.create(
                tipo='desconexion',
                descripcion=(
                    f'El ESP32 {disp.identificador} '
                    f'({disp.laboratorio.nombre if disp.laboratorio_id else "sin lab"}) '
                    f'se ha desconectado. {detalle}'
                ),
                nivel='critico',
                content_type=ctype,
                object_id=disp.id,
            )
        log.info(f"[Scheduler] Auto-desconexión — {len(obsoletos)} ESP32 marcados 'desconectado' + alertas HU-25.")
    except Exception as e:
        log.error(f"[Scheduler] Error en auto-desconexión de ESP32: {e}", exc_info=True)


def _tarea_alerta_equipo_sin_ocupacion():
    """HU-26 — Detecta laboratorios vacíos con equipos encendidos."""
    try:
        from django.contrib.contenttypes.models import ContentType
        from apps.laboratorio.models import Laboratorio
        from apps.equipos.models import Equipo
        from apps.ocupacion.models import EventoOcupacion
        from apps.alertas.models import Alerta

        ctype_lab = ContentType.objects.get_for_model(Laboratorio)
        for lab in Laboratorio.objects.filter(estado='activo'):
            ultimo = (EventoOcupacion.objects
                      .filter(dispositivo__laboratorio=lab)
                      .order_by('-timestamp').first())
            lab_vacio = (ultimo is None) or (ultimo.estado == 'vacio')
            if not lab_vacio:
                continue

            equipos_encendidos = Equipo.objects.filter(
                laboratorio=lab, activo=True, estado_conexion='activo'
            ).count()
            if equipos_encendidos == 0:
                continue

            ya_alertado = Alerta.objects.filter(
                tipo='equipo_sin_ocupacion', object_id=lab.id,
                content_type=ctype_lab, leida=False
            ).exists()
            if ya_alertado:
                continue

            Alerta.objects.create(
                tipo='equipo_sin_ocupacion',
                descripcion=(
                    f'El laboratorio {lab.nombre} está vacío pero tiene '
                    f'{equipos_encendidos} equipo(s) encendido(s).'
                ),
                nivel='medio',
                content_type=ctype_lab,
                object_id=lab.id,
            )
    except Exception as e:
        log.error(f"[Scheduler] Error en alerta equipo sin ocupación: {e}", exc_info=True)


def iniciar_scheduler():
    global _scheduler

    if _scheduler and _scheduler.running:
        log.warning("[Scheduler] Ya está corriendo, se omite el inicio duplicado.")
        return

    _scheduler = BackgroundScheduler(timezone='America/Guayaquil')

    _scheduler.add_job(
        _tarea_evaluar_reglas,
        trigger=IntervalTrigger(minutes=INTERVALO_MINUTOS),
        id='evaluar_reglas', name='Evaluación de reglas de automatización',
        replace_existing=True, next_run_time=datetime.now(_scheduler.timezone)
    )

    _scheduler.add_job(
        _tarea_ping_equipos,
        trigger=IntervalTrigger(minutes=PING_INTERVALO_MINUTOS),
        id='ping_equipos', name='Ping automático a equipos IPv4',
        replace_existing=True, next_run_time=datetime.now(_scheduler.timezone)
    )

    _scheduler.add_job(
        _tarea_marcar_esp32_desconectados,
        trigger=IntervalTrigger(minutes=ESP32_CHECK_INTERVALO_MINUTOS),
        id='esp32_desconexion', name='Auto-desconexión de ESP32 sin heartbeat',
        replace_existing=True, next_run_time=datetime.now(_scheduler.timezone)
    )

    _scheduler.add_job(
        _tarea_alerta_equipo_sin_ocupacion,
        trigger=IntervalTrigger(minutes=ESP32_CHECK_INTERVALO_MINUTOS),
        id='equipo_sin_ocupacion', name='Alerta de equipo activo sin ocupación',
        replace_existing=True, next_run_time=datetime.now(_scheduler.timezone)
    )

    _scheduler.start()
    log.info(
        f"[Scheduler] Iniciado — reglas cada {INTERVALO_MINUTOS} min, "
        f"ping cada {PING_INTERVALO_MINUTOS} min, auto-desconexión ESP32 cada "
        f"{ESP32_CHECK_INTERVALO_MINUTOS} min (timeout {ESP32_TIMEOUT_MINUTOS} min), "
        f"alerta equipo sin ocupación cada {ESP32_CHECK_INTERVALO_MINUTOS} min. "
        f"Zona horaria: America/Guayaquil"
    )


def detener_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log.info("[Scheduler] Detenido.")