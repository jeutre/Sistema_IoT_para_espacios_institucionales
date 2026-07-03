"""
apps/automatizacion/apps.py

Inicia el scheduler automáticamente cuando Django arranca.
APScheduler corre dentro del mismo proceso — no necesita Redis ni Celery.
"""

from django.apps import AppConfig


class AutomatizacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.automatizacion'
    verbose_name       = 'Automatización'

    def ready(self):
        """
        Se ejecuta una sola vez cuando Django termina de cargar.
        Arranca el scheduler de fondo que evalúa las reglas cada 5 minutos.
        """
        # Evitar doble arranque en desarrollo (Django carga apps dos veces con runserver)
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from .scheduler import iniciar_scheduler
        iniciar_scheduler()