from django.urls import path, include


urlpatterns = [
    path('laboratorio/',    include('apps.laboratorio.urls')),
    path('auth/',           include('apps.autenticacion.urls_api')),
    path('dispositivos/',   include('apps.dispositivos.urls')),
    path('equipos/',        include('apps.equipos.urls')),
    path('ocupacion/',      include('apps.ocupacion.urls')),
    path('dashboard/',      include('apps.dashboard.urls')),
    path('alertas/',        include('apps.alertas.urls')),
    path('reportes/',       include('apps.reportes.urls')),
    path('control/',        include('apps.control.urls')),
    path('automatizacion/', include('apps.automatizacion.urls')),
]