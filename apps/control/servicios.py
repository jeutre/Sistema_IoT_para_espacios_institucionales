"""
control/servicios.py

Servicio que envía comandos de apagado/suspensión al agente Windows
instalado en cada PC del laboratorio. (HU-19, HU-20)

Flujo:
  Django  →  POST http://<ip_pc>:8765/comando  →  Agente Windows
                                                        ↓
                                               shutdown /s  o  suspend
                                                        ↓
                                              {"exito": true/false}
"""

import requests
from django.utils import timezone

from apps.equipos.models import Equipo
from .models import Comando

# Puerto donde escucha el agente en cada PC
AGENTE_PUERTO  = 8765
AGENTE_TIMEOUT = 10  # segundos — si la PC no responde en 10s, fallido


def enviar_comando_a_equipo(equipo: Equipo, tipo_accion: str) -> Comando:
    """
    Crea un Comando en la BD y lo envía al agente Windows instalado en el equipo.
    Devuelve el Comando con su estado actualizado (ejecutado / fallido).

    Uso:
        from apps.control.servicios import enviar_comando_a_equipo
        cmd = enviar_comando_a_equipo(equipo, 'apagar_equipo')
    """
    # 1. Registrar el intento en la BD
    comando = Comando.objects.create(
        equipo=equipo,
        tipo_accion=tipo_accion,
        ip_equipo_destino=equipo.ip,
        estado='pendiente'
    )

    # 2. Enviar al agente
    url = f"http://{equipo.ip}:{AGENTE_PUERTO}/comando"
    try:
        response = requests.post(
            url,
            json={"accion": tipo_accion},
            timeout=AGENTE_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            exito = data.get('exito', False)
            comando.estado      = 'ejecutado' if exito else 'fallido'
            comando.resultado   = data.get('mensaje', '')
        else:
            comando.estado    = 'fallido'
            comando.resultado = f'HTTP {response.status_code}: {response.text[:200]}'

    except requests.exceptions.ConnectionError:
        comando.estado    = 'fallido'
        comando.resultado = 'No se pudo conectar al agente. ¿Está instalado y corriendo?'

    except requests.exceptions.Timeout:
        comando.estado    = 'fallido'
        comando.resultado = f'Timeout: el agente no respondió en {AGENTE_TIMEOUT}s.'

    except Exception as e:
        comando.estado    = 'fallido'
        comando.resultado = f'Error inesperado: {str(e)}'

    # 3. Actualizar BD con resultado
    comando.ejecutado_en = timezone.now()
    comando.save()

    return comando


def apagar_equipos_laboratorio(laboratorio_id: int) -> list:
    """
    Apaga TODOS los equipos activos de un laboratorio. (HU-20)
    Retorna lista de resultados por equipo.
    """
    equipos = Equipo.objects.filter(
        laboratorio__id=laboratorio_id,
        activo=True,
        estado_conexion='activo'
    )

    resultados = []
    for equipo in equipos:
        cmd = enviar_comando_a_equipo(equipo, 'apagar_equipo')
        resultados.append({
            'equipo':    equipo.nombre,
            'ip':        equipo.ip,
            'estado':    cmd.estado,
            'resultado': cmd.resultado,
        })

    return resultados


def suspender_equipos_laboratorio(laboratorio_id: int) -> list:
    """
    Suspende TODOS los equipos activos de un laboratorio. (HU-19)
    Retorna lista de resultados por equipo.
    """
    equipos = Equipo.objects.filter(
        laboratorio__id=laboratorio_id,
        activo=True,
        estado_conexion='activo'
    )

    resultados = []
    for equipo in equipos:
        cmd = enviar_comando_a_equipo(equipo, 'suspender_equipo')
        resultados.append({
            'equipo':    equipo.nombre,
            'ip':        equipo.ip,
            'estado':    cmd.estado,
            'resultado': cmd.resultado,
        })

    return resultados