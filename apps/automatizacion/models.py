"""
apps/automatizacion/models.py

CAMBIOS (Hallazgo crítico 1 y 2 del informe de avance, HU-28/HU-29):

1. CONDICION_CHOICES ahora incluye 'ocupacion_detectada', además de la
   'inactividad_minutos' que ya existía. Antes SOLO existía la condición de
   inactividad, por lo que era imposible configurar una regla que reaccione
   a "se detectó presencia" — que es justo lo que necesitan HU-20B
   (encender por relay) y HU-29 (encender iluminación).

2. Se agregan hora_inicio / hora_fin (HU-28: "configura horarios de
   funcionamiento del laboratorio"). Si ambos están definidos, la regla
   solo se evalúa dentro de esa ventana horaria.

3. Se agregan accion_secundaria / valor_umbral_secundario (HU-28: "tiempo
   de espera antes de suspender" + "tiempo adicional antes del apagado
   total"). Permite definir, en UNA sola regla de inactividad, una acción
   inicial (p. ej. suspender_equipo a los 15 min) y una acción posterior
   más agresiva (p. ej. apagar_equipo a los 45 min), sin tener que crear
   dos reglas independientes.
"""
from django.db import models


class ReglaAutomatizacion(models.Model):
    CONDICION_CHOICES = [
        ('inactividad_minutos', 'Minutos sin movimiento (PIR)'),
        ('ocupacion_detectada', 'Presencia detectada (PIR)'),
    ]

    ACCION_CHOICES = [
        ('apagar_equipo', 'Apagar equipo (PC)'),
        ('suspender_equipo', 'Suspender equipo (PC)'),
        ('apagar_luces', 'Apagar iluminación (ESP32)'),
        ('encender_luces', 'Encender iluminación (ESP32)'),
        ('encender_relay', 'Encender equipo por relay (ESP32)'),
    ]

    nombre = models.CharField(max_length=100)
    condicion = models.CharField(max_length=50, choices=CONDICION_CHOICES)
    valor_umbral = models.IntegerField(
        help_text="Minutos. Para 'inactividad_minutos': tiempo sin movimiento "
                   "antes de disparar accion_a_ejecutar. Para "
                   "'ocupacion_detectada': antigüedad máxima (en minutos) del "
                   "último evento 'ocupado' para considerarlo una detección "
                   "reciente."
    )
    accion_a_ejecutar = models.CharField(
        max_length=50, choices=ACCION_CHOICES,
        help_text="Acción principal (Ej: apagar_luces, encender_relay)."
    )
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    # ── HU-28: horario institucional de la regla ──────────────────────────
    hora_inicio = models.TimeField(
        null=True, blank=True,
        help_text="Si se define junto con hora_fin, la regla solo se evalúa "
                   "dentro de este horario (hora local América/Guayaquil)."
    )
    hora_fin = models.TimeField(
        null=True, blank=True,
        help_text="Ver hora_inicio."
    )

    # ── HU-28: acción secundaria (dos niveles de severidad) ────────────────
    accion_secundaria = models.CharField(
        max_length=50, choices=ACCION_CHOICES, null=True, blank=True,
        help_text="Opcional. Acción más agresiva a ejecutar cuando se supera "
                   "valor_umbral_secundario (Ej: pasar de suspender_equipo a "
                   "apagar_equipo tras más tiempo de inactividad)."
    )
    valor_umbral_secundario = models.IntegerField(
        null=True, blank=True,
        help_text="Minutos de inactividad para disparar accion_secundaria. "
                   "Debe ser mayor a valor_umbral. Solo aplica con "
                   "condicion='inactividad_minutos'."
    )

    class Meta:
        verbose_name = 'Regla de Automatización'
        verbose_name_plural = 'Reglas de Automatización'

    def __str__(self):
        return f"{self.nombre} ({'Activa' if self.activa else 'Inactiva'})"

    def dentro_de_horario(self, hora_actual):
        """
        HU-28. True si la regla aplica en este momento según su horario
        configurado. Si no se definió horario, siempre aplica.
        `hora_actual` es un datetime.time (hora local).
        """
        if not self.hora_inicio or not self.hora_fin:
            return True
        if self.hora_inicio <= self.hora_fin:
            return self.hora_inicio <= hora_actual <= self.hora_fin
        # Ventana que cruza medianoche (ej: 22:00 a 06:00)
        return hora_actual >= self.hora_inicio or hora_actual <= self.hora_fin
