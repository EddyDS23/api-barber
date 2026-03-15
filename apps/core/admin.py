from django.contrib import admin
from .models import BusinessSettings, BusinessHours, Holiday, NotificationSettings


@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'phone', 'email', 'booking_enabled']
    # No permitir crear ni borrar, solo editar el registro existente
    def has_add_permission(self, request):
        return not BusinessSettings.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['get_day_of_week_display', 'is_working', 'opening_time', 'closing_time']
    ordering = ['day_of_week']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['date', 'reason', 'created_at']
    ordering = ['date']


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['sms_reminder_enabled', 'whatsapp_enabled', 'whatsapp_connected']
    def has_add_permission(self, request):
        return not NotificationSettings.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False