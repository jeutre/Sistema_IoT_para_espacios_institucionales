from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crea el usuario admin si no existe'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
            self.stdout.write(self.style.SUCCESS('✓ Usuario admin creado exitosamente'))
        else:
            self.stdout.write(self.style.WARNING('⚠ Usuario admin ya existe'))
