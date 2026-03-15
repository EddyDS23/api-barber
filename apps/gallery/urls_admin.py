# ✅ Correcto (rutas específicas ANTES del router)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GalleryCategoryAdminViewSet, GalleryAdminViewSet

categories_router = DefaultRouter()
categories_router.register(r'', GalleryCategoryAdminViewSet, basename='admin-gallery-category')

router = DefaultRouter()
router.register(r'images', GalleryAdminViewSet, basename='admin-gallery')  # ← cambiar a 'images'

urlpatterns = [
    path('categories/', include(categories_router.urls)),
    path('', include(router.urls)),
]