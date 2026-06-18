from rest_framework.routers import DefaultRouter
from .views import EquipoViewSet

router = DefaultRouter()
router.register(r'', EquipoViewSet, basename='equipo')

urlpatterns = router.urls