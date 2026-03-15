from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BarberAdminViewSet, SpecialtyAdminViewSet, specialty_list

# Router de especialidades
specialties_router = DefaultRouter()
specialties_router.register(r'', SpecialtyAdminViewSet, basename='admin-specialties')

# Router principal de barberos
router = DefaultRouter()
router.register(r'', BarberAdminViewSet, basename='admin-barbers')

urlpatterns = [
    # Rutas fijas ANTES del router principal
    path('specialties/', include(specialties_router.urls)),  # ← primero
    path('', include(router.urls)),                          # ← después
]

