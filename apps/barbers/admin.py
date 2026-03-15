from django.contrib import admin
from .models import BarberStatus, Specialty, Barber, BarberSpecialty


@admin.register(BarberStatus)
class BarberStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color_code', 'description']
    search_fields = ['name']


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']


class BarberSpecialtyInline(admin.TabularInline):
    """
    Muestra las especialidades del barbero directamente
    dentro del formulario del barbero
    """
    model = BarberSpecialty
    extra = 1  # Muestra 1 fila vacía para agregar nueva especialidad


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'nickname', 'phone', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'nickname', 'phone']
    inlines = [BarberSpecialtyInline]  # ← reemplaza filter_horizontal


@admin.register(BarberSpecialty)
class BarberSpecialtyAdmin(admin.ModelAdmin):
    list_display = ['barber', 'specialty', 'created_at']