from django.urls import path
from .views import ExportarCSVView

urlpatterns = [
    path('exportar/<str:tipo>/', ExportarCSVView.as_view(), name='exportar-csv'),
]
