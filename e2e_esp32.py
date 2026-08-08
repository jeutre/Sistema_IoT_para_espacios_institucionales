#!/usr/bin/env python3
"""
VERIFICADOR END-TO-END CON ESP32 FÍSICO
=======================================

A diferencia de `manage.py test` (BD aislada, ping simulado), este script prueba
el sistema REAL: servidor Django corriendo + ESP32 encendido en la misma red.

NO inserta ni postea datos falsos. Solo:
  - se autentica como admin (JWT real),
  - hace PING REAL al ESP32 (el servidor ejecuta ping ICMP al aparato),
  - OBSERVA la ocupación mientras un humano dispara el sensor PIR,
    confirmando que llegan eventos reales enviados por el firmware.

Requisitos en la máquina donde lo corres:
  pip install requests

Uso típico (desde la PC donde corre el backend, con el ESP32 encendido):
  python e2e_esp32.py \
      --base-url http://192.168.1.10:8000 \
      --admin-user admin --admin-pass TU_CLAVE \
      --dispositivo-id 1 --equipo-id 1

Modos:
  (por defecto)      corre TODO, incluida la observación del PIR (interactivo).
  --check-only       solo login + ping (sin esperar el sensor). Útil para sanity.
  --pir-timeout N    segundos a esperar el disparo del PIR (default 60).
"""
import argparse
import sys
import time

try:
    import requests
except ImportError:
    print("Falta 'requests'. Instálalo con:  pip install requests")
    sys.exit(2)


# --- salida bonita sin dependencias ---
def ok(msg):    print(f"  [ \033[92mPASS\033[0m ] {msg}")
def fail(msg):  print(f"  [ \033[91mFALLA\033[0m ] {msg}")
def info(msg):  print(f"  [ .... ] {msg}")
def head(msg):  print(f"\n=== {msg} ===")


class Estado:
    def __init__(self):
        self.pasos = []
    def registrar(self, nombre, passed):
        self.pasos.append((nombre, passed))
        (ok if passed else fail)(nombre)
        return passed
    def resumen(self):
        p = sum(1 for _, x in self.pasos if x)
        head(f"RESUMEN: {p}/{len(self.pasos)} verificaciones OK")
        for nombre, x in self.pasos:
            print(f"   {'✓' if x else '✗'} {nombre}")
        return p == len(self.pasos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', default='http://localhost:8000')
    ap.add_argument('--admin-user', required=True)
    ap.add_argument('--admin-pass', required=True)
    ap.add_argument('--dispositivo-id', type=int, required=True,
                    help='ID del ESP32 registrado en el sistema')
    ap.add_argument('--equipo-id', type=int, default=None,
                    help='ID de un equipo IPv4 para probar ping (opcional)')
    ap.add_argument('--check-only', action='store_true',
                    help='Solo login + ping, sin esperar el PIR')
    ap.add_argument('--pir-timeout', type=int, default=60)
    args = ap.parse_args()

    base = args.base_url.rstrip('/')
    api = f"{base}/api/v1"
    st = Estado()

    # ------------------------------------------------------------------
    head("1) LOGIN ADMIN (HU-01)  — JWT real")
    try:
        r = requests.post(f"{api}/auth/token/",
                          json={'username': args.admin_user, 'password': args.admin_pass},
                          timeout=10)
    except requests.RequestException as e:
        fail(f"No se pudo contactar al servidor en {base}  ({e})")
        print("\n¿Está corriendo Django y es accesible esa IP/puerto desde aquí?")
        sys.exit(1)

    if not st.registrar("Login admin devuelve token", r.status_code == 200 and 'access' in r.json()):
        print(f"       respuesta: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    token = r.json()['access']
    H = {'Authorization': f'Bearer {token}'}

    # ------------------------------------------------------------------
    head("2) EL ESP32 ESTÁ REGISTRADO (HU-06)")
    r = requests.get(f"{api}/dispositivos/esp32/{args.dispositivo_id}/", headers=H, timeout=10)
    existe = r.status_code == 200
    st.registrar(f"Dispositivo id={args.dispositivo_id} existe", existe)
    if existe:
        d = r.json()
        info(f"identificador={d.get('identificador')}  ip={d.get('ip')}  estado_previo={d.get('estado')}")
    else:
        print(f"       {r.status_code} {r.text[:200]}")
        sys.exit(1)

    # ------------------------------------------------------------------
    head("3) PING REAL AL ESP32 (HU-07)  — el servidor hace ping ICMP al aparato")
    info("El ESP32 debe estar ENCENDIDO y en la misma red...")
    r = requests.get(f"{api}/dispositivos/esp32/{args.dispositivo_id}/ping/", headers=H, timeout=15)
    st.registrar("El endpoint de ping responde 200 (no 500)", r.status_code == 200)
    if r.status_code == 200:
        body = r.json()
        info(f"respuesta real: conectado={body.get('conectado')}  estado={body.get('estado')}")
        conectado = body.get('estado') == 'conectado'
        if not st.registrar("El ESP32 responde al ping (está encendido)", conectado):
            print("       -> Si esperabas que estuviera encendido, revisa alimentación/WiFi/IP.")

    # ------------------------------------------------------------------
    if args.equipo_id:
        head("4) PING REAL A EQUIPO IPv4 (HU-14)")
        r = requests.get(f"{api}/equipos/{args.equipo_id}/ping/", headers=H, timeout=15)
        if st.registrar("Ping de equipo responde 200", r.status_code == 200):
            b = r.json()
            info(f"equipo={b.get('equipo')}  responde={b.get('responde')}  estado={b.get('estado_conexion')}")

    if args.check_only:
        print()
        sys.exit(0 if st.resumen() else 1)

    # ------------------------------------------------------------------
    head("5) OCUPACIÓN EN VIVO DESDE EL PIR (HU-09/10/11)  — datos REALES del sensor")

    def contar_eventos():
        rr = requests.get(f"{api}/ocupacion/?dispositivo={args.dispositivo_id}", headers=H, timeout=10)
        return rr.json().get('count', 0) if rr.status_code == 200 else -1

    def estado_tiempo_real():
        rr = requests.get(f"{api}/ocupacion/tiempo-real/", headers=H, timeout=10)
        if rr.status_code != 200:
            return None
        for x in rr.json():
            if x.get('dispositivo') == d.get('identificador'):
                return x.get('estado')
        return None

    base_count = contar_eventos()
    info(f"Eventos de ocupación actuales para este dispositivo: {base_count}")
    print()
    print("  >>> AHORA: pasa la mano frente al sensor PIR y luego aléjate. <<<")
    print(f"      (esperando hasta {args.pir_timeout}s a que el ESP32 envíe datos reales)")
    print()

    t0 = time.time()
    nuevos = 0
    vio_ocupado = False
    while time.time() - t0 < args.pir_timeout:
        c = contar_eventos()
        if c > base_count:
            nuevos = c - base_count
            er = estado_tiempo_real()
            if er == 'ocupado':
                vio_ocupado = True
            info(f"  eventos nuevos={nuevos}  estado_tiempo_real={er}")
            if nuevos >= 1 and vio_ocupado:
                break
        time.sleep(2)

    st.registrar("Llegaron eventos NUEVOS del PIR (no inyectados)", nuevos >= 1)
    st.registrar("El sensor reportó 'ocupado' al detectar movimiento", vio_ocupado)

    # ------------------------------------------------------------------
    head("6) HISTORIAL DE COMUNICACIÓN CRECIÓ (HU-08)")
    r = requests.get(f"{api}/dispositivos/historial/?dispositivo={args.dispositivo_id}",
                     headers=H, timeout=10)
    if r.status_code == 200:
        total = r.json().get('count', len(r.json()) if isinstance(r.json(), list) else 0)
        info(f"registros de comunicación: {total}")

    print()
    sys.exit(0 if st.resumen() else 1)


if __name__ == '__main__':
    main()