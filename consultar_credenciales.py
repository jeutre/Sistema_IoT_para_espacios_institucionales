import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.dispositivos.models import Dispositivo
from rest_framework_api_key.models import APIKey
from apps.laboratorio.models import Laboratorio
from apps.equipos.models import Equipo

print('=== LABORATORIOS ===')
for lab in Laboratorio.objects.all():
    print(f'ID: {lab.id} | {lab.nombre} | Ubicación: {lab.ubicacion}')

print('\n=== DISPOSITIVOS REGISTRADOS ===')
for d in Dispositivo.objects.all():
    print(f'ID: {d.id} | {d.identificador} | IP: {d.ip} | Estado: {d.estado}')

print('\n=== EQUIPOS ===')
count = Equipo.objects.count()
print(f'Total: {count} equipos')
for e in Equipo.objects.all()[:3]:
    print(f'ID: {e.id} | {e.nombre} | IP: {e.ip} | Estado: {e.estado_conexion}')

print('\n=== API KEYS ===')
for key in APIKey.objects.all():
    print(f'Nombre: {key.name}')
    print(f'  Prefix: {key.prefix}...')
    print(f'  Creada: {key.created}')
    print(f'  Válida: {"Sí" if key.is_valid else "No"}')
