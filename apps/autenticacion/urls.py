from django.urls import path
from . import views
print(">>> cargando autenticacion/urls.py")


urlpatterns = [
    path('login/',   views.login_view,   name='login'),
    path('logout/',  views.logout_view,  name='logout'),
    path('perfil/',  views.perfil_view,  name='perfil'),
]