from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comando',
            name='origen',
            field=models.CharField(
                choices=[
                    ('manual', 'Manual (administrador)'),
                    ('automatico', 'Automático (motor de reglas)'),
                ],
                default='manual',
                max_length=20,
            ),
        ),
    ]
