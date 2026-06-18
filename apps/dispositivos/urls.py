from rest_framework.routers import DefaultRouter
from .views import DispositivoViewSet, HistorialComunicacionViewSet

router = DefaultRouter()
router.register(r'esp32',     DispositivoViewSet,          basename='dispositivo')
router.register(r'historial', HistorialComunicacionViewSet, basename='historial')

urlpatterns = router.urls