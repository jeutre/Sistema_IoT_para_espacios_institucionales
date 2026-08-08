from django.urls import path
from .views import (
    EventoOcupacionViewSet,
    RecibirPIRView,
    OcupacionTiempoRealView,
    HorasPicoView,
)

ocupacion_list = EventoOcupacionViewSet.as_view({'get': 'list'})
ocupacion_detail = EventoOcupacionViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    # HU-09 — ESP32 envía datos PIR (protegido por API Key)
    path('pir/', RecibirPIRView.as_view(), name='recibir-pir'),

    # HU-10 — Ocupación en tiempo real
    path('tiempo-real/', OcupacionTiempoRealView.as_view(), name='ocupacion-tiempo-real'),

    # HU-12 — Horas pico de ocupación
    path('horas-pico/', HorasPicoView.as_view(), name='horas-pico'),

    # HU-11 — Historial de ocupación
    path('', ocupacion_list, name='ocupacion-list'),
    path('<int:pk>/', ocupacion_detail, name='ocupacion-detail'),
]