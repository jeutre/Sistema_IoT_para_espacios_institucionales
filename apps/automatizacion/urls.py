from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReglaAutomatizacionViewSet, trigger_evaluacion

router = DefaultRouter()
router.register(r'reglas', ReglaAutomatizacionViewSet, basename='reglas')

urlpatterns = [
    path('evaluar/', trigger_evaluacion, name='evaluar-reglas'),
    path('', include(router.urls)),
]
