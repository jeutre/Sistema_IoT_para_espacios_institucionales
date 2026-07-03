"""
apps/automatizacion/scheduler.py

Scheduler que evalúa las reglas de automatización cada 5 minutos.
Usa APScheduler en modo background — corre dentro del proceso Django.

Instalar: pip install apscheduler
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings

log = logging.getLogger(__name__)

# Intervalo configurable desde settings.py
# Por defecto: 5 minutos. Cambiar en settings: AUTOMATIZACION_INTERVALO_MINUTOS = 10
INTERVALO_MINUTOS = getattr(settings, 'AUTOMATIZACION_INTERVALO_MINUTOS', 5)

_scheduler = None


def _tarea_evaluar_reglas():
    """
    Tarea que ejecuta el scheduler cada X minutos.
    Llama al motor de reglas y registra el resultado.
    """
    try:
        # Import dentro de la función para evitar imports circulares al arrancar Django
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
        # Nunca dejar que una excepción mate el scheduler
        log.error(f"[Scheduler] Error en evaluación de reglas: {e}", exc_info=True)


def iniciar_scheduler():
    """
    Inicia el scheduler de fondo. Se llama desde AutomatizacionConfig.ready().
    Solo se puede iniciar una vez — si ya está corriendo, no hace nada.
    """
    global _scheduler

    if _scheduler and _scheduler.running:
        log.warning("[Scheduler] Ya está corriendo, se omite el inicio duplicado.")
        return

    _scheduler = BackgroundScheduler(timezone='America/Guayaquil')

    _scheduler.add_job(
        _tarea_evaluar_reglas,
        trigger=IntervalTrigger(minutes=INTERVALO_MINUTOS),
        id='evaluar_reglas',
        name='Evaluación de reglas de automatización',
        replace_existing=True,
        # Ejecutar inmediatamente al arrancar Django, no esperar el primer intervalo
        next_run_time=None
    )

    _scheduler.start()
    log.info(
        f"[Scheduler] Iniciado — evaluando reglas cada {INTERVALO_MINUTOS} minutos. "
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