from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicePublicViewSet

router = DefaultRouter()
router.register(r'', ServicePublicViewSet, basename='public-services')

urlpatterns = [
    path('', include(router.urls))
]