#!/usr/bin/env python3
"""
SCRIPT DE SETUP — Crea datos iniciales y genera las credenciales del ESP32
===========================================================================

Este script automatiza la creación de:
1. Laboratorios de prueba
2. Dispositivos ESP32
3. Equipos IPv4
4. API Key para que el ESP32 reporte datos

Uso:
  python setup_datos_iniciales.py

Resultado:
  Se imprime el comando para ejecutar el simulador ESP32 con las credenciales generadas.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.laboratorio.models import Laboratorio
from apps.dispositivos.models import Dispositivo
from apps.equipos.models import Equipo
from rest_framework_api_key.models import APIKey

User = get_user_model()

print("\n" + "="*70)
print("SETUP INICIAL — Poblando base de datos de prueba")
print("="*70 + "\n")

# ── 1. Crear laboratorios ────────────────────────────────────────────────────
print("[1/4] Creando laboratorios...")
laboratorios_data = [
    {'nombre': 'Laboratorio de Redes', 'ubicacion': 'Bloque A - Piso 2', 'capacidad': 30},
    {'nombre': 'Laboratorio de Programación', 'ubicacion': 'Bloque B - Piso 1', 'capacidad': 25},
    {'nombre': 'Laboratorio de IoT', 'ubicacion': 'Bloque C - Piso 3', 'capacidad': 20},
]

labs_creados = []
for data in laboratorios_data:
    lab, created = Laboratorio.objects.get_or_create(
        nombre=data['nombre'],
        defaults={'ubicacion': data['ubicacion'], 'capacidad': data['capacidad'], 'activo': True}
    )
    labs_creados.append(lab)
    status = "✓ CREADO" if created else "⊘ YA EXISTE"
    print(f"  {status}: {lab.nombre} (ID: {lab.id})")

# ── 2. Crear dispositivos ESP32 ──────────────────────────────────────────────
print("\n[2/4] Registrando ESP32...")
esp32_data = [
    {
        'identificador': 'ESP32-LAB-01',
        'ip': '192.168.1.60',
        'mac_address': '24:6F:28:AA:BB:01',
        'laboratorio': labs_creados[0]
    },
    {
        'identificador': 'ESP32-LAB-02',
        'ip': '192.168.1.61',
        'mac_address': '24:6F:28:AA:BB:02',
        'laboratorio': labs_creados[1]
    },
    {
        'identificador': 'ESP32-LAB-03',
        'ip': '192.168.1.62',
        'mac_address': '24:6F:28:AA:BB:03',
        'laboratorio': labs_creados[2]
    },
]

esp32_creados = []
for data in esp32_data:
    disp, created = Dispositivo.objects.get_or_create(
        identificador=data['identificador'],
        defaults={
            'ip': data['ip'],
            'mac_address': data['mac_address'],
            'laboratorio': data['laboratorio'],
            'estado': 'desconectado'
        }
    )
    esp32_creados.append(disp)
    status = "✓ CREADO" if created else "⊘ YA EXISTE"
    print(f"  {status}: {disp.identificador} (ID: {disp.id}) - IP: {disp.ip}")

# ── 3. Crear equipos IPv4 ────────────────────────────────────────────────────
print("\n[3/4] Registrando equipos IPv4...")
equipos_data = [
    {'nombre': 'PC-LAB01-001', 'ip': '192.168.1.100', 'mac': 'AA:BB:CC:DD:00:01', 'laboratorio': labs_creados[0]},
    {'nombre': 'PC-LAB01-002', 'ip': '192.168.1.101', 'mac': 'AA:BB:CC:DD:00:02', 'laboratorio': labs_creados[0]},
    {'nombre': 'PC-LAB02-001', 'ip': '192.168.1.110', 'mac': 'AA:BB:CC:DD:01:01', 'laboratorio': labs_creados[1]},
    {'nombre': 'PC-LAB03-001', 'ip': '192.168.1.120', 'mac': 'AA:BB:CC:DD:02:01', 'laboratorio': labs_creados[2]},
]

for data in equipos_data:
    equipo, created = Equipo.objects.get_or_create(
        nombre=data['nombre'],
        defaults={
            'ip': data['ip'],
            'mac': data['mac'],
            'laboratorio': data['laboratorio'],
            'activo': True,
            'estado_conexion': 'inactivo'
        }
    )
    status = "✓ CREADO" if created else "⊘ YA EXISTE"
    print(f"  {status}: {equipo.nombre} (ID: {equipo.id}) - IP: {equipo.ip}")

# ── 4. Crear/recuperar API Key ───────────────────────────────────────────────
print("\n[4/4] Configurando API Key del ESP32...")
api_key_name = 'esp32-default'
try:
    # Intentar recuperar la key existente
    api_key_obj = APIKey.objects.get(name=api_key_name)
    print(f"  ⊘ YA EXISTE: {api_key_name}")
    # Crear una nueva entrada de autenticación (no podemos recuperar la key original por seguridad)
    api_key_obj, key_string = APIKey.objects.create_key(name=api_key_name + '-new')
    print(f"  ✓ NUEVA CREADA: {api_key_name}-new")
except APIKey.DoesNotExist:
    api_key_obj, key_string = APIKey.objects.create_key(name=api_key_name)
    print(f"  ✓ CREADA: {api_key_name}")

# ── Resumen e instrucciones ──────────────────────────────────────────────────
print("\n" + "="*70)
print("SETUP COMPLETADO ✓")
print("="*70)

print(f"\n📊 RESUMEN:")
print(f"  • Laboratorios: {len(labs_creados)}")
print(f"  • Dispositivos ESP32: {len(esp32_creados)}")
print(f"  • Equipos IPv4: {len(equipos_data)}")
print(f"  • API Key: {api_key_name}")

print(f"\n🚀 PRÓXIMO PASO: Ejecuta el SIMULADOR ESP32 con este comando:")
print(f"\n  python esp32_simulador.py \\")
print(f"      --base-url http://localhost:8000 \\")
print(f"      --dispositivo-id {esp32_creados[0].id} \\")
print(f"      --api-key {key_string} \\")
print(f"      --interval 10 \\")
print(f"      --modo realistic")

print(f"\n📍 Notas:")
print(f"  • Reemplaza {esp32_creados[0].id} con cualquier ID de los ESP32 creados si quieres probar otro")
print(f"  • La API Key es: {key_string}")
print(f"  • El dashboard en http://localhost:5173/dashboard se actualizará cada 10 segundos")
print(f"  • Presiona Ctrl+C en el simulador para detenerlo")
print()
