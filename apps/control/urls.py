from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComandoViewSet

router = DefaultRouter()
router.register(r'comandos', ComandoViewSet, basename='comando')

urlpatterns = [
    path('', include(router.urls)),
]
