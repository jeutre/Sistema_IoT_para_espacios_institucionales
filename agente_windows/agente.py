"""
agente_windows/agente.py

Agente ligero que corre como servicio de Windows en cada PC del laboratorio.
Recibe comandos de Django vía HTTP y los ejecuta localmente.

Instalación (ejecutar como Administrador):
    python instalar_servicio.py install
    python instalar_servicio.py start

Puerto: 8765 (configurable abajo)
"""

import subprocess
import logging
import json
import ctypes
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── Configuración ─────────────────────────────────────────────────────────────
PUERTO          = 8765
# IP del servidor Django — SOLO acepta comandos de esta IP
# Cambiar por la IP real del servidor Django en la red del laboratorio
IP_DJANGO       = os.environ.get('DJANGO_SERVER_IP', '192.168.1.100')
LOG_FILE        = os.path.join(os.path.dirname(__file__), 'agente.log')

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)


# ── Comandos Windows ──────────────────────────────────────────────────────────
def apagar():
    """Apaga la PC inmediatamente. (HU-20)"""
    log.info("Ejecutando: APAGADO")
    subprocess.run(['shutdown', '/s', '/t', '0'], check=True)


def suspender():
    """
    Suspende la PC (sleep/hibernate). (HU-19)
    rundll32 powrprof.dll,SetSuspendState 0,1,0
      args: Hibernate=0, ForceCritical=1, DisableWakeEvent=0
    """
    log.info("Ejecutando: SUSPENSIÓN")
    subprocess.run(
        ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'],
        check=True
    )


# Mapa de acciones disponibles
ACCIONES = {
    'apagar_equipo':    apagar,
    'suspender_equipo': suspender,
}


# ── Handler HTTP ──────────────────────────────────────────────────────────────
class AgenteHandler(BaseHTTPRequestHandler):

    def _responder(self, codigo: int, cuerpo: dict):
        body = json.dumps(cuerpo).encode('utf-8')
        self.send_response(codigo)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # ── Validación de IP origen ───────────────────────────────────────────
        ip_cliente = self.client_address[0]
        if ip_cliente != IP_DJANGO:
            log.warning(f"Solicitud rechazada de IP no autorizada: {ip_cliente}")
            self._responder(403, {
                'exito':   False,
                'mensaje': 'IP no autorizada.'
            })
            return

        if self.path != '/comando':
            self._responder(404, {'exito': False, 'mensaje': 'Ruta no encontrada.'})
            return

        # ── Leer body ─────────────────────────────────────────────────────────
        try:
            longitud = int(self.headers.get('Content-Length', 0))
            body     = self.rfile.read(longitud)
            datos    = json.loads(body)
        except Exception as e:
            log.error(f"Error leyendo body: {e}")
            self._responder(400, {'exito': False, 'mensaje': 'Body inválido.'})
            return

        accion = datos.get('accion', '').strip()

        if accion not in ACCIONES:
            log.warning(f"Acción desconocida recibida: {accion}")
            self._responder(400, {
                'exito':   False,
                'mensaje': f'Acción desconocida: {accion}. '
                           f'Válidas: {list(ACCIONES.keys())}'
            })
            return

        # ── Ejecutar acción ───────────────────────────────────────────────────
        try:
            log.info(f"Comando recibido de {ip_cliente}: {accion}")
            ACCIONES[accion]()
            self._responder(200, {
                'exito':   True,
                'mensaje': f'Acción "{accion}" ejecutada correctamente.'
            })
        except subprocess.CalledProcessError as e:
            log.error(f"Error ejecutando {accion}: {e}")
            self._responder(500, {
                'exito':   False,
                'mensaje': f'Error al ejecutar {accion}: {str(e)}'
            })

    def log_message(self, format, *args):
        # Silencia los logs de HTTP por defecto — usamos nuestro propio logger
        pass


# ── Servidor ──────────────────────────────────────────────────────────────────
def iniciar_servidor():
    servidor = HTTPServer(('0.0.0.0', PUERTO), AgenteHandler)
    log.info(f"Agente IoT iniciado en puerto {PUERTO}. IP Django autorizada: {IP_DJANGO}")
    print(f"[Agente IoT] Escuchando en puerto {PUERTO}...")
    servidor.serve_forever()


if __name__ == '__main__':
    iniciar_servidor()