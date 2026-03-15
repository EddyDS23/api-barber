from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,LogoutView,UserProfileView
)


urlpatterns = [
    # Iniciar sesión → retorna access + refresh tokens
    path('login/', LoginView.as_view(), name='auth-login'),

    # Renovar access token usando el refresh token
    # Esta view ya viene lista en simplejwt, no necesitamos crearla
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),

    # Cerrar sesión → invalida el refresh token
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    # Datos del usuario actual
    path('me/', UserProfileView.as_view(), name='auth-me')

]