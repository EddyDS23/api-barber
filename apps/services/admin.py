from django.contrib import admin
from .models import ServiceType, Service, ServiceBarber


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'display_order', 'created_at']
    search_fields = ['name']
    ordering = ['display_order']


class ServiceBarberInline(admin.TabularInline):
    """
    Muestra los barberos asignados al servicio
    directamente dentro del formulario del servicio
    """
    model = ServiceBarber
    extra = 1  # Muestra 1 fila vacía para agregar nuevo barbero


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'duration', 'service_type', 'is_active']
    list_filter = ['service_type', 'is_active']
    search_fields = ['name']
    inlines = [ServiceBarberInline]  # ← reemplaza filter_horizontal


@admin.register(ServiceBarber)
class ServiceBarberAdmin(admin.ModelAdmin):
    list_display = ['service', 'barber', 'created_at']