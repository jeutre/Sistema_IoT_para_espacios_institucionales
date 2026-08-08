from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import SesionUsuario


# Re-registramos User con un admin más amigable (sin alterar el esquema).
admin.site.unregister(User)


@admin.register(User)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_active', 'last_login']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']


@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'ip', 'inicio', 'fecha_fin', 'activa']
    list_filter = ['activa']
    search_fields = ['usuario__username']
    readonly_fields = ['inicio']