from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientAdminViewSet

router = DefaultRouter()
router.register(r'', ClientAdminViewSet, basename='admin-clients')

urlpatterns = [
    path('', include(router.urls)),
]


