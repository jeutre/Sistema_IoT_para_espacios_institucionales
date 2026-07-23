from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    # Tradicional
    path('login/',   views.login_view,   name='login'),
    path('logout/',  views.logout_view,  name='logout'),
    path('perfil/',  views.perfil_view,  name='perfil'),
    path('register/', views.register_view, name='register'),
    
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]