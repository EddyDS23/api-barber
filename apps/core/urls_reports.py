# apps/core/urls_reports.py

from django.urls import path
from .views_reports import (
    ReportIncomeChartView,
    ReportTopServicesView,
    ReportTopBarbersView,
    ReportOccupancyHeatmapView,
)

"""
URLs resultantes bajo /api/admin/reports/:

  GET /api/admin/reports/income-chart/?period=today|week
  GET /api/admin/reports/top-services/
  GET /api/admin/reports/top-barbers/
  GET /api/admin/reports/occupancy-heatmap/
"""

urlpatterns = [
    path('income-chart/',      ReportIncomeChartView.as_view(),        name='report-income-chart'),
    path('top-services/',      ReportTopServicesView.as_view(),        name='report-top-services'),
    path('top-barbers/',       ReportTopBarbersView.as_view(),         name='report-top-barbers'),
    path('occupancy-heatmap/', ReportOccupancyHeatmapView.as_view(),   name='report-occupancy-heatmap'),
]