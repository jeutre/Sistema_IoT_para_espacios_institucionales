"""
Genera datos históricos realistas para la demostración del sistema.

Uso:
    python manage.py seed_demo
    python manage.py seed_demo --reset          # borra los datos previos
    python manage.py seed_demo --semanas 8

Genera:
    · 2 laboratorios
    · 2 dispositivos ESP32
    · 20 equipos (PC-01 .. PC-20)
    · ~2000 eventos de ocupación distribuidos en 6 semanas
    · eventos de conexión/desconexión de equipos
    · heartbeats de las últimas 24 h
    · alertas de ejemplo de los 3 tipos
    · comandos ejecutados (alimenta HU-31, HU-32 y el reporte energético HU-35)
    · 2 reglas de automatización

NOTA TÉCNICA: los campos de fecha de estos modelos usan auto_now_add=True,
así que Django ignora cualquier valor que se les pase al crear. Por eso el
comando desactiva temporalmente esa bandera (ver _fechas_manuales).
Es la única forma de sembrar histórico sin tocar los modelos.
"""
import random
from contextlib import contextmanager
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.laboratorio.models import Laboratorio
from apps.dispositivos.models import Dispositivo, HistorialComunicacion
from apps.ocupacion.models import EventoOcupacion
from apps.equipos.models import Equipo, EventoConexion
from apps.alertas.models import Alerta
from apps.control.models import Comando
from apps.automatizacion.models import ReglaAutomatizacion


@contextmanager
def _fechas_manuales(*pares):
    """
    Desactiva auto_now_add en los campos indicados mientras dure el bloque.
    Uso: with _fechas_manuales((EventoOcupacion, 'registrado_en'), ...):
    """
    originales = []
    for modelo, nombre in pares:
        campo = modelo._meta.get_field(nombre)
        originales.append((campo, campo.auto_now_add))
        campo.auto_now_add = False
    try:
        yield
    finally:
        for campo, valor in originales:
            campo.auto_now_add = valor


class Command(BaseCommand):
    help = 'Siembra datos históricos realistas para la demo del sistema IoT.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                            help='Borra todos los datos antes de sembrar.')
        parser.add_argument('--semanas', type=int, default=6,
                            help='Semanas de histórico a generar (por defecto 6).')

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(2026)  # reproducible: la demo siempre sale igual
        semanas = options['semanas']

        if options['reset']:
            self._reset()

        labs = self._crear_laboratorios()
        dispositivos = self._crear_dispositivos(labs)
        equipos = self._crear_equipos(labs)
        n_ocup = self._crear_ocupacion(dispositivos, semanas)
        n_conex = self._crear_eventos_equipos(equipos, semanas)
        n_hb = self._crear_heartbeats(dispositivos)
        n_alertas = self._crear_alertas(equipos, dispositivos)
        n_cmd = self._crear_comandos(equipos, dispositivos, semanas)
        self._crear_reglas()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Datos sembrados correctamente:'))
        self.stdout.write(f'  · Laboratorios ............ {len(labs)}')
        self.stdout.write(f'  · Dispositivos ESP32 ...... {len(dispositivos)}')
        self.stdout.write(f'  · Equipos ................. {len(equipos)}')
        self.stdout.write(f'  · Eventos de ocupación .... {n_ocup}')
        self.stdout.write(f'  · Eventos de conexión ..... {n_conex}')
        self.stdout.write(f'  · Heartbeats .............. {n_hb}')
        self.stdout.write(f'  · Alertas ................. {n_alertas}')
        self.stdout.write(f'  · Comandos ejecutados ..... {n_cmd}')
        self.stdout.write('')
        self.stdout.write('Verifica en el navegador:')
        self.stdout.write('  /api/v1/ocupacion/horas-pico/')
        self.stdout.write('  /api/v1/dashboard/resumen/')

    # ── borrado ──────────────────────────────────────────────────────────
    def _reset(self):
        self.stdout.write(self.style.WARNING('Borrando datos existentes...'))
        for modelo in (Comando, Alerta, EventoConexion, HistorialComunicacion,
                       EventoOcupacion, Equipo, Dispositivo,
                       ReglaAutomatizacion, Laboratorio):
            modelo.objects.all().delete()

    # ── catálogo base ────────────────────────────────────────────────────
    def _crear_laboratorios(self):
        datos = [
            ('Laboratorio de Redes A', 'Bloque B - Piso 2', 30),
            ('Laboratorio de Software', 'Bloque B - Piso 3', 25),
        ]
        labs = []
        for nombre, ubicacion, capacidad in datos:
            lab, _ = Laboratorio.objects.get_or_create(
                nombre=nombre,
                defaults={'ubicacion': ubicacion, 'capacidad': capacidad, 'activo': True},
            )
            labs.append(lab)
        return labs

    def _crear_dispositivos(self, labs):
        datos = [
            (labs[0], 'ESP32-LAB-01', 'A4:CF:12:8B:3D:01', '192.168.1.50'),
            (labs[1], 'ESP32-LAB-02', 'A4:CF:12:8B:3D:02', '192.168.1.51'),
        ]
        dispositivos = []
        for lab, ident, mac, ip in datos:
            d, _ = Dispositivo.objects.get_or_create(
                identificador=ident,
                defaults={
                    'laboratorio': lab, 'mac_address': mac, 'ip': ip,
                    'estado': 'conectado',
                    'ultima_conexion': timezone.now() - timedelta(minutes=2),
                },
            )
            dispositivos.append(d)
        return dispositivos

    def _crear_equipos(self, labs):
        equipos = []
        for i in range(1, 21):
            lab = labs[0] if i <= 12 else labs[1]
            activo = random.random() < 0.65
            equipo, creado = Equipo.objects.get_or_create(
                ip=f'192.168.1.{100 + i}',
                defaults={
                    'laboratorio': lab,
                    'nombre': f'PC-{i:02d}',
                    'mac': f'B8:27:EB:{i:02X}:4F:9A',
                    'activo': True,
                    'estado_conexion': 'activo' if activo else 'inactivo',
                    'ultimo_ping': timezone.now() - timedelta(
                        minutes=random.randint(1, 4) if activo else random.randint(45, 900)
                    ),
                },
            )
            equipos.append(equipo)
        return equipos

    # ── ocupación (HU-11, HU-12, HU-23) ──────────────────────────────────
    def _crear_ocupacion(self, dispositivos, semanas):
        """
        Simula un horario académico real: más carga entre 08:00-11:00 y
        14:00-17:00, laboratorio vacío en la noche y los fines de semana.
        Emite un evento 'ocupado' cada ~10 min mientras hay presencia,
        que es lo que consume el histograma de horas pico (HU-12).
        """
        ahora = timezone.now()
        inicio = ahora - timedelta(weeks=semanas)
        # Probabilidad de que el laboratorio esté ocupado en cada hora
        perfil = {
            7: 0.30, 8: 0.85, 9: 0.95, 10: 0.90, 11: 0.75, 12: 0.35,
            13: 0.20, 14: 0.80, 15: 0.90, 16: 0.85, 17: 0.60,
            18: 0.40, 19: 0.30, 20: 0.15,
        }

        eventos = []
        for dispositivo in dispositivos:
            dia = inicio
            while dia < ahora:
                if dia.weekday() < 5:  # lunes a viernes
                    for hora, probabilidad in perfil.items():
                        if random.random() > probabilidad:
                            continue
                        base = timezone.localtime(dia).replace(hour=hora, minute=0, second=0, microsecond=0)
                        # 4 a 6 lecturas de presencia dentro de la hora
                        for _ in range(random.randint(4, 6)):
                            momento = base + timedelta(minutes=random.randint(0, 59))
                            if momento < ahora:
                                eventos.append(EventoOcupacion(
                                    dispositivo=dispositivo,
                                    estado='ocupado',
                                    registrado_en=momento,
                                ))
                    # marca de aula vacía al cierre
                cierre = timezone.localtime(dia).replace(hour=21, minute=random.randint(0, 20))
                if cierre < ahora:
                        eventos.append(EventoOcupacion(
                            dispositivo=dispositivo, estado='vacio', registrado_en=cierre,
                        ))
                dia += timedelta(days=1)

        # estado actual coherente con la hora de la demo
        estado_actual = 'ocupado' if 7 <= timezone.localtime(ahora).hour <= 20 else 'vacio'
        for dispositivo in dispositivos:
            eventos.append(EventoOcupacion(
                dispositivo=dispositivo, estado=estado_actual,
                registrado_en=ahora - timedelta(minutes=3),
            ))

        with _fechas_manuales((EventoOcupacion, 'registrado_en')):
            EventoOcupacion.objects.bulk_create(eventos, batch_size=500)
        return len(eventos)

    # ── eventos de conexión de equipos (HU-17, HU-18) ────────────────────
    def _crear_eventos_equipos(self, equipos, semanas):
        ahora = timezone.now()
        eventos = []
        for equipo in equipos:
            momento = ahora - timedelta(weeks=semanas)
            tipo = 'conexion'
            while momento < ahora:
                momento += timedelta(hours=random.randint(6, 40))
                if momento >= ahora:
                    break
                eventos.append(EventoConexion(
                    equipo=equipo, tipo=tipo, registrado_en=momento,
                ))
                tipo = 'desconexion' if tipo == 'conexion' else 'conexion'

        with _fechas_manuales((EventoConexion, 'registrado_en')):
            EventoConexion.objects.bulk_create(eventos, batch_size=500)
        return len(eventos)

    # ── heartbeats (HU-07, HU-08) ────────────────────────────────────────
    def _crear_heartbeats(self, dispositivos):
        ahora = timezone.now()
        registros = []
        for dispositivo in dispositivos:
            for minutos in range(0, 24 * 60, 5):
                registros.append(HistorialComunicacion(
                    dispositivo=dispositivo,
                    mensaje='heartbeat',
                    recibido_en=ahora - timedelta(minutes=minutos),
                ))

        with _fechas_manuales((HistorialComunicacion, 'recibido_en')):
            HistorialComunicacion.objects.bulk_create(registros, batch_size=500)
        return len(registros)

    # ── alertas (HU-24 a HU-27) ──────────────────────────────────────────
    def _crear_alertas(self, equipos, dispositivos):
        ahora = timezone.now()
        plantillas = [
            ('desconexion', 'medio',
             'El equipo {} dejó de responder al ping durante más de 10 minutos.'),
            ('movimiento', 'critico',
             'Movimiento detectado en {} a las 23:412 h, fuera del horario permitido.'),
            ('error_sistema', 'bajo',
             'El dispositivo {} reportó una lectura inconsistente del sensor PIR.'),
        ]
        alertas = []
        for i in range(18):
            tipo, nivel, texto = plantillas[i % 3]
            objetivo = (equipos[i % len(equipos)].nombre if tipo == 'desconexion'
                        else dispositivos[i % len(dispositivos)].laboratorio.nombre)
            alertas.append(Alerta(
                tipo=tipo, nivel=nivel,
                descripcion=texto.format(objetivo).replace('23:412', '23:41'),
                leida=i > 5,
                creado_en=ahora - timedelta(hours=random.randint(1, 480)),
            ))

        with _fechas_manuales((Alerta, 'creado_en')):
            Alerta.objects.bulk_create(alertas)
        return len(alertas)

    # ── comandos ejecutados (HU-31, HU-32, HU-35) ────────────────────────
    def _crear_comandos(self, equipos, dispositivos, semanas):
        """
        Estos registros son los que alimentan el reporte de optimización
        energética: cada apagado automático es ahorro medible.
        """
        ahora = timezone.now()
        comandos = []
        for _ in range(120):
            momento = ahora - timedelta(
                minutes=random.randint(0, semanas * 7 * 24 * 60)
            )
            accion = random.choice([
                'apagar_luces', 'apagar_luces', 'apagar_luces',
                'encender_luces', 'suspender_equipo', 'apagar_equipo',
            ])
            si_es_equipo = accion in ('suspender_equipo', 'apagar_equipo')
            equipo = random.choice(equipos) if si_es_equipo else None
            comandos.append(Comando(
                equipo=equipo,
                dispositivo=None if si_es_equipo else random.choice(dispositivos),
                tipo_accion=accion,
                estado='ejecutado' if random.random() < 0.92 else 'fallido',
                ip_equipo_destino=equipo.ip if equipo else None,
                resultado='OK' if random.random() < 0.92 else 'Sin respuesta del agente',
                creado_en=momento,
                ejecutado_en=momento + timedelta(seconds=random.randint(2, 30)),
            ))

        with _fechas_manuales((Comando, 'creado_en')):
            Comando.objects.bulk_create(comandos, batch_size=200)
        return len(comandos)

    # ── reglas (HU-28) ───────────────────────────────────────────────────
    def _crear_reglas(self):
        reglas = [
            ('Apagar luces por inactividad', 'inactividad_minutos', 30, 'apagar_luces'),
            ('Suspender equipos por inactividad', 'inactividad_minutos', 45, 'suspender_equipo'),
        ]
        for nombre, condicion, umbral, accion in reglas:
            ReglaAutomatizacion.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'condicion': condicion,
                    'valor_umbral': umbral,
                    'accion_a_ejecutar': accion,
                    'activa': True,
                },
            )