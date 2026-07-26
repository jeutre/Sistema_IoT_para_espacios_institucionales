from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .serializers import MiTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MiTokenObtainPairView(TokenObtainPairView):
    serializer_class = MiTokenObtainPairSerializer


urlpatterns = [
    path('login/',   views.login_view,   name='login'),
    path('logout/',  views.logout_view,  name='logout'),
    path('perfil/',  views.perfil_view,  name='perfil'),
    path('register/', views.register_view, name='register'),

    path('token/', MiTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]