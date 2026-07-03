"""
automatizacion/servicios.py

Motor de reglas que evalúa condiciones y ejecuta acciones automáticamente.
Se llama desde el endpoint manual /api/v1/automatizacion/evaluar/
y desde el scheduler (Opción C pendiente).
"""

from datetime import timedelta
from django.utils import timezone

from apps.automatizacion.models import ReglaAutomatizacion
from apps.dispositivos.models import Dispositivo
from apps.ocupacion.models import EventoOcupacion
from apps.equipos.models import Equipo
from apps.control.models import Comando
from apps.control.servicios import enviar_comando_a_equipo


def evaluar_reglas() -> dict:
    """
    Evalúa todas las reglas activas y ejecuta acciones si se cumplen.

    Para comandos ESP32 (luces/relay): crea el Comando en BD y el ESP32
    lo consulta en su próximo ciclo de polling.

    Para comandos PC (apagar/suspender): llama directamente al agente
    Windows instalado en cada PC.

    Retorna un resumen de lo ejecutado.
    """
    reglas = ReglaAutomatizacion.objects.filter(activa=True)
    ahora  = timezone.now()

    resumen = {
        'reglas_evaluadas':   0,
        'comandos_esp32':     0,
        'comandos_pc':        0,
        'comandos_fallidos':  0,
    }

    for regla in reglas:
        resumen['reglas_evaluadas'] += 1

        if regla.condicion != 'inactividad_minutos':
            continue

        umbral_tiempo = ahora - timedelta(minutes=regla.valor_umbral)
        accion        = regla.accion_a_ejecutar

        # ── Comandos para ESP32 (luces, relay) ───────────────────────────────
        if accion in ('apagar_luces', 'encender_luces', 'encender_relay'):
            dispositivos = Dispositivo.objects.filter(estado='conectado')

            for disp in dispositivos:
                ultimo = EventoOcupacion.objects.filter(
                    dispositivo=disp
                ).order_by('-registrado_en').first()

                if not ultimo or ultimo.registrado_en >= umbral_tiempo:
                    continue

                # Anti-spam: no crear si ya hay un comando pendiente igual
                ya_existe = Comando.objects.filter(
                    dispositivo=disp,
                    tipo_accion=accion,
                    estado='pendiente'
                ).exists()

                if not ya_existe:
                    Comando.objects.create(
                        dispositivo=disp,
                        tipo_accion=accion
                    )
                    resumen['comandos_esp32'] += 1

        # ── Comandos para PCs (apagar, suspender) vía agente Windows ─────────
        elif accion in ('apagar_equipo', 'suspender_equipo'):
            dispositivos = Dispositivo.objects.filter(estado='conectado')

            for disp in dispositivos:
                ultimo = EventoOcupacion.objects.filter(
                    dispositivo=disp
                ).order_by('-registrado_en').first()

                if not ultimo or ultimo.registrado_en >= umbral_tiempo:
                    continue

                # Obtener equipos activos del mismo laboratorio que el ESP32
                equipos = Equipo.objects.filter(
                    laboratorio=disp.laboratorio,
                    activo=True,
                    estado_conexion='activo'
                )

                for equipo in equipos:
                    # Anti-spam: no reenviar si ya se intentó recientemente
                    ya_existe = Comando.objects.filter(
                        equipo=equipo,
                        tipo_accion=accion,
                        creado_en__gte=ahora - timedelta(minutes=5)
                    ).exists()

                    if ya_existe:
                        continue

                    # Enviar al agente Windows directamente
                    cmd = enviar_comando_a_equipo(equipo, accion)

                    if cmd.estado == 'ejecutado':
                        resumen['comandos_pc'] += 1
                    else:
                        resumen['comandos_fallidos'] += 1

    return resumen