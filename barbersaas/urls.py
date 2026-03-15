"""
URL configuration for barbersaas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    #-- Autenticacion
    path('api/admin/auth/', include('apps.authentication.urls')),  

    #-- Endpoints Publicos

    #Barberos
    path('api/public/team/', include('apps.barbers.urls')),

    #Servicios
    path('api/public/services/', include('apps.services.urls')),

    #Galeria
    path('api/public/gallery/', include('apps.gallery.urls')),

    #Citas
    path('api/public/appointments/', include('apps.appointments.urls')),

    #-- Endpoints Admin

    #Barberos
    path('api/admin/barbers/', include('apps.barbers.urls_admin')),

    #Servicios
    path('api/admin/services/', include('apps.services.urls_admin')),

    #Clientes
    path('api/admin/clients/', include('apps.clients.urls_admin')),

    #Galeria
    path('api/admin/gallery/', include('apps.gallery.urls_admin')),

    #Dashboard
    path('api/admin/dashboard/', include('apps.core.urls_dashboard')),

    #Finanzas
    path('api/admin/finance/', include('apps.finance.urls_admin')),

    #Reportes
    path('api/admin/reports/', include('apps.core.urls_reports')),

    #Citas
    path('api/admin/agenda/', include('apps.appointments.urls_admin')),

    #Configuraciones y Notificaciones
    path('api/admin/settings/', include('apps.core.urls_settings')),

    #-- Documentacion
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

