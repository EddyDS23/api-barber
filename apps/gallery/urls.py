from django.urls import path, include 
from rest_framework.routers import DefaultRouter

from .views import GalleryPublicViewSet

router = DefaultRouter()
router.register(r'', GalleryPublicViewSet, basename='public-gallery')

urlpatterns = [
    path('', include(router.urls)),
]



