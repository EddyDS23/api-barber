# apps/appointments/urls_admin.py

from django.urls import path
from .views_admin import (
    AgendaScheduleView,
    AgendaAppointmentDetailView,
    AgendaChangeStatusView,
    AgendaQuickAppointmentView,
)

"""
URLs resultantes bajo /api/admin/agenda/:

  GET   /api/admin/agenda/schedule/?date=YYYY-MM-DD
  GET   /api/admin/agenda/appointments/{id}/
  PATCH /api/admin/agenda/appointments/{id}/change-status/
  POST  /api/admin/agenda/quick-appointment/
"""

urlpatterns = [
    # Vista de la matriz del día
    path('schedule/',
         AgendaScheduleView.as_view(),
         name='agenda-schedule'),

    # Detalle de cita (para el modal)
    path('appointments/<int:pk>/',
         AgendaAppointmentDetailView.as_view(),
         name='agenda-appointment-detail'),

    # Cambiar estado de cita
    path('appointments/<int:pk>/change-status/',
         AgendaChangeStatusView.as_view(),
         name='agenda-change-status'),

    # Crear cita rápida desde slot vacío
    path('quick-appointment/',
         AgendaQuickAppointmentView.as_view(),
         name='agenda-quick-appointment'),
]