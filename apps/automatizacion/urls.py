from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReglaAutomatizacionViewSet,
    trigger_evaluacion,
    estado_scheduler,
    historial_automatizaciones,
)

router = DefaultRouter()
router.register(r'reglas', ReglaAutomatizacionViewSet, basename='reglas')

urlpatterns = [
    path('evaluar/',    trigger_evaluacion,          name='evaluar-reglas'),
    path('scheduler/',  estado_scheduler,            name='estado-scheduler'),
    path('historial/',  historial_automatizaciones,  name='historial-automatizaciones'),  # HU-32
    path('',            include(router.urls)),
]
