"""
agente_windows/instalar_servicio.py

Instala el agente como servicio de Windows usando pywin32.
Requiere: pip install pywin32

Uso (ejecutar como Administrador en cada PC):
    python instalar_servicio.py install   ← instala el servicio
    python instalar_servicio.py start     ← inicia el servicio
    python instalar_servicio.py stop      ← detiene el servicio
    python instalar_servicio.py remove    ← desinstala el servicio
    python instalar_servicio.py status    ← muestra el estado actual
"""

import sys
import os
import subprocess

NOMBRE_SERVICIO     = 'AgenteIoT'
DESCRIPCION         = 'Agente IoT — Recibe comandos de apagado y suspensión del sistema IoT institucional.'
RUTA_AGENTE         = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agente.py')
PYTHON_EXE          = sys.executable  # Python que está corriendo este script


def _sc(args: list) -> tuple[int, str]:
    """Ejecuta un comando sc.exe y retorna (código, salida)."""
    resultado = subprocess.run(
        ['sc'] + args,
        capture_output=True, text=True
    )
    return resultado.returncode, resultado.stdout + resultado.stderr


def instalar():
    binpath = f'"{PYTHON_EXE}" "{RUTA_AGENTE}"'
    codigo, salida = _sc([
        'create', NOMBRE_SERVICIO,
        'binPath=', binpath,
        'start=', 'auto',
        'DisplayName=', NOMBRE_SERVICIO
    ])
    if codigo == 0:
        # Agregar descripción
        _sc(['description', NOMBRE_SERVICIO, DESCRIPCION])
        print(f'✓ Servicio "{NOMBRE_SERVICIO}" instalado correctamente.')
        print('  Ahora ejecuta: python instalar_servicio.py start')
    else:
        print(f'✗ Error instalando servicio:\n{salida}')


def iniciar():
    codigo, salida = _sc(['start', NOMBRE_SERVICIO])
    if codigo == 0:
        print(f'✓ Servicio "{NOMBRE_SERVICIO}" iniciado.')
    else:
        print(f'✗ Error iniciando servicio:\n{salida}')


def detener():
    codigo, salida = _sc(['stop', NOMBRE_SERVICIO])
    if codigo == 0:
        print(f'✓ Servicio "{NOMBRE_SERVICIO}" detenido.')
    else:
        print(f'✗ Error deteniendo servicio:\n{salida}')


def desinstalar():
    detener()
    codigo, salida = _sc(['delete', NOMBRE_SERVICIO])
    if codigo == 0:
        print(f'✓ Servicio "{NOMBRE_SERVICIO}" eliminado.')
    else:
        print(f'✗ Error eliminando servicio:\n{salida}')


def estado():
    codigo, salida = _sc(['query', NOMBRE_SERVICIO])
    print(salida)


def abrir_firewall():
    """
    Abre el puerto 8765 en el firewall de Windows para que Django
    pueda conectarse al agente. Ejecutar una vez por PC.
    """
    resultado = subprocess.run([
        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
        'name=AgenteIoT',
        'protocol=TCP',
        'dir=in',
        'localport=8765',
        'action=allow'
    ], capture_output=True, text=True)

    if resultado.returncode == 0:
        print('✓ Puerto 8765 abierto en el firewall.')
    else:
        print(f'✗ Error abriendo firewall:\n{resultado.stdout}{resultado.stderr}')


COMANDOS = {
    'install': instalar,
    'start':   iniciar,
    'stop':    detener,
    'remove':  desinstalar,
    'status':  estado,
    'firewall': abrir_firewall,
}

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(f'Uso: python instalar_servicio.py [{"|".join(COMANDOS)}]')
        sys.exit(1)

    # Verificar que corre como Administrador
    try:
        import ctypes
        es_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        es_admin = False

    if not es_admin:
        print('✗ Este script debe ejecutarse como Administrador.')
        print('  Haz clic derecho en PowerShell → "Ejecutar como administrador"')
        sys.exit(1)

    COMANDOS[sys.argv[1]]()