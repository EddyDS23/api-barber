# apps/core/urls_dashboard.py

from django.urls import path
from .views_dashboard import (
    DashboardStatsView,
    DashboardWeeklyPerformanceView,
    DashboardUpcomingAppointmentsView,
)

"""
Todas estas URLs quedan bajo el prefijo /api/admin/dashboard/
que se define en barbershop/urls.py

Resultado final:
  GET /api/admin/dashboard/stats/
  GET /api/admin/dashboard/weekly-performance/
  GET /api/admin/dashboard/upcoming-appointments/?limit=5
"""

urlpatterns = [
    path('stats/',
         DashboardStatsView.as_view(),
         name='dashboard-stats'),

    path('weekly-performance/',
         DashboardWeeklyPerformanceView.as_view(),
         name='dashboard-weekly'),

    path('upcoming-appointments/',
         DashboardUpcomingAppointmentsView.as_view(),
         name='dashboard-upcoming'),
]