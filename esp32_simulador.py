#!/usr/bin/env python3
"""
SIMULADOR ESP32 — Emula un sensor PIR reportando ocupación en tiempo real
===========================================================================

Este script simula un ESP32 físico enviando datos de ocupación al backend.
Útil para validar el dashboard sin tener el hardware real conectado.

Uso:
  python esp32_simulador.py \
      --base-url http://localhost:8000 \
      --dispositivo-id 1 \
      --api-key TU_API_KEY_AQUI \
      --interval 15

Parámetros:
  --base-url        URL del servidor Django (default: http://localhost:8000)
  --dispositivo-id  ID del ESP32 registrado en el sistema (requerido)
  --api-key         API Key del ESP32 (requerido)
  --interval        Segundos entre reportes (default: 15)
  --modo            'realistic' (alterna entre ocupado/vacio) o 'test' (todos ocupados)
"""

import argparse
import time
import random
import requests
import logging
from datetime import datetime

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)


def simular_ocupacion(modo='realistic'):
    """
    Genera un estado aleatorio de ocupación.
    
    Modos:
    - 'realistic': alterna entre ocupado/vacio con cierta probabilidad
    - 'test':      siempre devuelve 'ocupado'
    - 'alternado': alterna perfecto ocupado/vacio cada llamada
    """
    if modo == 'test':
        return 'ocupado'
    elif modo == 'alternado':
        return 'ocupado' if random.random() > 0.5 else 'vacio'
    else:  # realistic
        # En un laboratorio real, la ocupación es más frecuente que la inactividad
        # 70% de probabilidad de estar ocupado, 30% de estar vacío
        return 'ocupado' if random.random() < 0.7 else 'vacio'


def reportar_ocupacion(base_url, dispositivo_id, api_key, estado):
    """
    Envía un reporte de ocupación al backend.
    
    Retorna (success, message)
    """
    url = f"{base_url}/api/v1/ocupacion/pir/"
    headers = {
        'Authorization': f'Api-Key {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'dispositivo_id': dispositivo_id,
        'estado': estado
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5)
        if r.status_code == 201:
            return True, f"Reporte enviado: {estado}"
        else:
            return False, f"Error {r.status_code}: {r.text[:100]}"
    except requests.ConnectionError:
        return False, f"No se pudo conectar a {base_url}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='Simulador ESP32 IoT')
    parser.add_argument('--base-url', default='http://localhost:8000',
                        help='URL del servidor Django')
    parser.add_argument('--dispositivo-id', type=int, required=True,
                        help='ID del ESP32 registrado')
    parser.add_argument('--api-key', required=True,
                        help='API Key del ESP32')
    parser.add_argument('--interval', type=int, default=15,
                        help='Segundos entre reportes (default: 15)')
    parser.add_argument('--modo', default='realistic',
                        choices=['realistic', 'test', 'alternado'],
                        help='Modo de simulación')
    
    args = parser.parse_args()
    
    log.info(f"Iniciando simulador ESP32")
    log.info(f"  Servidor: {args.base_url}")
    log.info(f"  Dispositivo ID: {args.dispositivo_id}")
    log.info(f"  Intervalo: {args.interval}s")
    log.info(f"  Modo: {args.modo}")
    log.info(f"")
    log.info(f"Presiona Ctrl+C para detener.")
    log.info(f"")
    
    reportes_exitosos = 0
    reportes_fallidos = 0
    
    try:
        while True:
            estado = simular_ocupacion(args.modo)
            success, msg = reportar_ocupacion(
                args.base_url,
                args.dispositivo_id,
                args.api_key,
                estado
            )
            
            if success:
                reportes_exitosos += 1
                log.info(f"✓ {msg}")
            else:
                reportes_fallidos += 1
                log.error(f"✗ {msg}")
            
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        log.info("")
        log.info("Detenido por usuario.")
        log.info(f"Resumen: {reportes_exitosos} exitosos, {reportes_fallidos} fallidos")
        return 0


if __name__ == '__main__':
    exit(main())
