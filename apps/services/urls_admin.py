from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceAdminViewSet, ServiceTypeAdminViewSet

# Router separado para tipos
types_router = DefaultRouter()
types_router.register(r'', ServiceTypeAdminViewSet, basename='admin-service-types')

# Router principal para servicios
router = DefaultRouter()
router.register(r'', ServiceAdminViewSet, basename='admin-services')

urlpatterns = [
    # Tipos ANTES que el router principal
    path('types/', include(types_router.urls)),  # ← primero
    path('', include(router.urls)),              # ← después
]