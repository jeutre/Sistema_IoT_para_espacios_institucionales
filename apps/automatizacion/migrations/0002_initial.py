# Generado a mano para acompañar el cambio de apps/automatizacion/models.py
# (agrega condición por presencia, horario y acción secundaria — HU-28/HU-29)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automatizacion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reglaautomatizacion',
            name='condicion',
            field=models.CharField(
                choices=[
                    ('inactividad_minutos', 'Minutos sin movimiento (PIR)'),
                    ('ocupacion_detectada', 'Presencia detectada (PIR)'),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name='reglaautomatizacion',
            name='valor_umbral',
            field=models.IntegerField(
                help_text=(
                    "Minutos. Para 'inactividad_minutos': tiempo sin movimiento "
                    "antes de disparar accion_a_ejecutar. Para 'ocupacion_detectada': "
                    "antigüedad máxima (en minutos) del último evento 'ocupado' para "
                    "considerarlo una detección reciente."
                )
            ),
        ),
        migrations.AlterField(
            model_name='reglaautomatizacion',
            name='accion_a_ejecutar',
            field=models.CharField(
                choices=[
                    ('apagar_equipo', 'Apagar equipo (PC)'),
                    ('suspender_equipo', 'Suspender equipo (PC)'),
                    ('apagar_luces', 'Apagar iluminación (ESP32)'),
                    ('encender_luces', 'Encender iluminación (ESP32)'),
                    ('encender_relay', 'Encender equipo por relay (ESP32)'),
                ],
                help_text='Acción principal (Ej: apagar_luces, encender_relay).',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='reglaautomatizacion',
            name='hora_inicio',
            field=models.TimeField(
                blank=True, null=True,
                help_text=(
                    'Si se define junto con hora_fin, la regla solo se evalúa '
                    'dentro de este horario (hora local América/Guayaquil).'
                ),
            ),
        ),
        migrations.AddField(
            model_name='reglaautomatizacion',
            name='hora_fin',
            field=models.TimeField(blank=True, null=True, help_text='Ver hora_inicio.'),
        ),
        migrations.AddField(
            model_name='reglaautomatizacion',
            name='accion_secundaria',
            field=models.CharField(
                blank=True, null=True, max_length=50,
                choices=[
                    ('apagar_equipo', 'Apagar equipo (PC)'),
                    ('suspender_equipo', 'Suspender equipo (PC)'),
                    ('apagar_luces', 'Apagar iluminación (ESP32)'),
                    ('encender_luces', 'Encender iluminación (ESP32)'),
                    ('encender_relay', 'Encender equipo por relay (ESP32)'),
                ],
                help_text=(
                    'Opcional. Acción más agresiva a ejecutar cuando se supera '
                    'valor_umbral_secundario (Ej: pasar de suspender_equipo a '
                    'apagar_equipo tras más tiempo de inactividad).'
                ),
            ),
        ),
        migrations.AddField(
            model_name='reglaautomatizacion',
            name='valor_umbral_secundario',
            field=models.IntegerField(
                blank=True, null=True,
                help_text=(
                    'Minutos de inactividad para disparar accion_secundaria. '
                    'Debe ser mayor a valor_umbral. Solo aplica con '
                    "condicion='inactividad_minutos'."
                ),
            ),
        ),
    ]
