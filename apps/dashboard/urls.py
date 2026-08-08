from django.urls import path
from .views import DashboardResumenView, DashboardKPIsView

urlpatterns = [
    path('resumen/', DashboardResumenView.as_view(), name='dashboard-resumen'),
    path('kpis/', DashboardKPIsView.as_view(), name='dashboard-kpis'),
]
