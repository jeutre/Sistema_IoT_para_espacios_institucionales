from rest_framework.routers import DefaultRouter
from .views import EquipoViewSet, EventoConexionViewSet

router = DefaultRouter()
router.register(r'eventos-conexion', EventoConexionViewSet, basename='evento-conexion')
router.register(r'', EquipoViewSet, basename='equipo')

urlpatterns = router.urls