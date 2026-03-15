from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BarberPublicViewSet

#Router publico
router = DefaultRouter()
router.register(r'', BarberPublicViewSet, basename='public-barbers')

urlpatterns = [
    path('', include(router.urls)),
]
