from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DispositivoViewSet, HistorialComunicacionViewSet

router = DefaultRouter()
router.register('esp32', DispositivoViewSet, basename='dispositivo')
router.register('historial', HistorialComunicacionViewSet, basename='historial-comunicacion')

urlpatterns = [
    path('', include(router.urls)),
]