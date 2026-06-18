from rest_framework.routers import DefaultRouter
from .views import OcupacionViewSet

router = DefaultRouter()
router.register(r'', OcupacionViewSet, basename='ocupacion')

urlpatterns = router.urls