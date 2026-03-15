# apps/core/urls_settings.py

from django.urls import path
from .views_settings import (
    BusinessInfoView,
    UploadLogoView,
    BookingRulesView,
    BusinessHoursView,
    BusinessHoursDayView,
    HolidaysView,
    HolidayDeleteView,
    NotificationSettingsView,
)

"""
URLs resultantes bajo /api/admin/settings/:

  GET   /api/admin/settings/business-info/
  PATCH /api/admin/settings/business-info/
  POST  /api/admin/settings/upload-logo/

  GET   /api/admin/settings/booking-rules/
  PATCH /api/admin/settings/booking-rules/

  GET   /api/admin/settings/business-hours/
  PUT   /api/admin/settings/business-hours/

  GET   /api/admin/settings/holidays/
  POST  /api/admin/settings/holidays/
  DELETE /api/admin/settings/holidays/{id}/

  GET   /api/admin/settings/notifications/
  PATCH /api/admin/settings/notifications/
"""

urlpatterns = [
    # Apartado 1: Información General
    path('business-info/',  BusinessInfoView.as_view(),  name='settings-business-info'),
    path('upload-logo/',    UploadLogoView.as_view(),    name='settings-upload-logo'),

    # Apartado 2: Reglas de Reservas
    path('booking-rules/',  BookingRulesView.as_view(),  name='settings-booking-rules'),

    # Apartado 3: Horarios
    path('business-hours/', BusinessHoursView.as_view(), name='settings-business-hours'),
    path('business-hours/<int:day_of_week>/', BusinessHoursDayView.as_view(), name='settings-business-hours-day'),

    # Apartado 3b: Feriados
    path('holidays/',       HolidaysView.as_view(),      name='settings-holidays'),
    path('holidays/<int:pk>/', HolidayDeleteView.as_view(), name='settings-holiday-delete'),

    # Apartado 4: Notificaciones
    path('notifications/',  NotificationSettingsView.as_view(), name='settings-notifications'),
]