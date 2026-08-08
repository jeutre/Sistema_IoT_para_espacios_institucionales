import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

log = logging.getLogger(__name__)
Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Crea el usuario admin por defecto si no existe'

    def handle(self, *args, **options):
        admin_user = os.environ.get('ADMIN_USER', 'admin')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@tecnoecuatoriano.edu.ec')

        if not Usuario.objects.filter(username=admin_user).exists():
            Usuario.objects.create_superuser(
                username=admin_user,
                email=admin_email,
                password=admin_pass,
                rol='admin',
            )
            self.stdout.write(self.style.SUCCESS(
                f'✓ Admin "{admin_user}" creado exitosamente'
            ))
        else:
            self.stdout.write(f'Admin "{admin_user}" ya existe — omitido')