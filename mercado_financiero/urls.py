from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MercadoFinancieroViewSet

# Router para registrar ViewSets
router = DefaultRouter()
router.register(r'mercado-financiero', MercadoFinancieroViewSet, basename='mercado-financiero')

urlpatterns = [
    path('api/', include(router.urls)),
]

# URLs adicionales específicas (opcionales, ya que el ViewSet las maneja)
app_name = 'mercado_financiero'