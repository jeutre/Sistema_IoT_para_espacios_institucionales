from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipoViewSet, EventoConexionViewSet

router = DefaultRouter()
# IMPORTANTE: registrar 'eventos-conexion' ANTES del prefijo '' para que
# la URL /equipos/eventos-conexion/ no sea capturada por el detalle
# /equipos/<pk>/ del EquipoViewSet.
router.register('eventos-conexion', EventoConexionViewSet, basename='evento-conexion')
router.register('', EquipoViewSet, basename='equipo')

urlpatterns = [
    path('', include(router.urls)),
]