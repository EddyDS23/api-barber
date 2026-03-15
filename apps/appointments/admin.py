from django.contrib import admin
from .models import StatusAppointment, Appointment, AppointmentService


@admin.register(StatusAppointment)
class StatusAppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client', 'barber', 'date', 'time',
        'status', 'total_amount', 'confirmation_code'
    ]
    list_filter = ['status', 'barber', 'date']
    search_fields = ['client__full_name', 'confirmation_code']
    ordering = ['-date', '-time']
    # Solo lectura porque los totales se calculan automáticamente
    readonly_fields = ['total_amount', 'total_duration', 'confirmation_code']


@admin.register(AppointmentService)
class AppointmentServiceAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'service', 'price_snapshot', 'duration_snapshot']