"""
Utilidades para logging y monitoreo de dispositivos IoT
"""

import logging

# Configurar logger específico para IoT
iot_logger = logging.getLogger('iot')

def log_device_ping(device_id, ip, status, error=None):
    """
    Registra eventos de ping a dispositivos
    
    Args:
        device_id: Identificador del dispositivo
        ip: Dirección IP del dispositivo
        status: Estado del ping (conectado/desconectado/error)
        error: Detalle del error (opcional)
    """
    if status == 'conectado':
        iot_logger.info(f'Dispositivo {device_id} ({ip}) - Ping exitoso')
    elif status == 'desconectado':
        iot_logger.warning(f'Dispositivo {device_id} ({ip}) - Sin respuesta')
    elif status == 'error':
        iot_logger.error(f'Dispositivo {device_id} ({ip}) - Error: {error}')
    else:
        iot_logger.warning(f'Dispositivo {device_id} ({ip}) - Estado desconocido: {status}')

def log_device_connection_change(device_id, old_status, new_status):
    """
    Registra cambios de estado en dispositivos
    
    Args:
        device_id: Identificador del dispositivo
        old_status: Estado anterior
        new_status: Estado nuevo
    """
    if old_status != new_status:
        iot_logger.info(
            f'Dispositivo {device_id} - Cambio de estado: '
            f'{old_status} -> {new_status}'
        )

def log_iot_operation(operation, device_id=None, details=None):
    """
    Registra operaciones generales del sistema IoT
    
    Args:
        operation: Nombre de la operación
        device_id: Identificador del dispositivo (opcional)
        details: Detalles adicionales (opcional)
    """
    device_info = f' ({device_id})' if device_id else ''
    details_info = f' - {details}' if details else ''
    
    iot_logger.info(f'IoT{device_info} - {operation}{details_info}')