"""
apps/automatizacion/scheduler.py

Scheduler de fondo (APScheduler) que corre dentro del proceso Django.
Ejecuta dos tareas periódicas:
  1. Evaluación de reglas de automatización (cada AUTOMATIZACION_INTERVALO_MINUTOS).
  2. Ping automático a todos los equipos IPv4 (cada PING_INTERVALO_MINUTOS). (HU-14)

Instalar: pip install apscheduler
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
# Cambiar en settings: PING_INTERVALO_MINUTOS = 5
PING_INTERVALO_MINUTOS = getattr(settings, 'PING_INTERVALO_MINUTOS', 2)

_scheduler = None


def _tarea_evaluar_reglas():
    """
    Evalúa las reglas de automatización cada X minutos.
    """
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
    """
    Hace ping automáticamente a todos los equipos activos y actualiza su estado. (HU-14)
    Registra un EventoConexion solo cuando un equipo cambia de estado. (HU-17)
    Los pings corren en paralelo (hilos) para que N equipos tarden casi lo mismo que 1.
    """
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


def iniciar_scheduler():
    """
    Inicia el scheduler de fondo. Se llama desde AutomatizacionConfig.ready().
    """
    global _scheduler

    if _scheduler and _scheduler.running:
        log.warning("[Scheduler] Ya está corriendo, se omite el inicio duplicado.")
        return

    _scheduler = BackgroundScheduler(timezone='America/Guayaquil')

    # Job 1: evaluación de reglas de automatización
    _scheduler.add_job(
        _tarea_evaluar_reglas,
        trigger=IntervalTrigger(minutes=INTERVALO_MINUTOS),
        id='evaluar_reglas',
        name='Evaluación de reglas de automatización',
        replace_existing=True,
        next_run_time=datetime.now(_scheduler.timezone)
    )

    # Job 2: ping automático a equipos IPv4 (HU-14)
    _scheduler.add_job(
        _tarea_ping_equipos,
        trigger=IntervalTrigger(minutes=PING_INTERVALO_MINUTOS),
        id='ping_equipos',
        name='Ping automático a equipos IPv4',
        replace_existing=True,
        next_run_time=datetime.now(_scheduler.timezone)
    )

    _scheduler.start()
    log.info(
        f"[Scheduler] Iniciado — reglas cada {INTERVALO_MINUTOS} min, "
        f"ping de equipos cada {PING_INTERVALO_MINUTOS} min. "
        f"Zona horaria: America/Guayaquil"
    )


def detener_scheduler():
    """
    Detiene el scheduler limpiamente. Útil para tests y shutdown.
    """
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log.info("[Scheduler] Detenido.")