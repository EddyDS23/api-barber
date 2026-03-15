# apps/finance/urls_admin.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FinanceSummaryView,
    FinancialTransactionViewSet,
    TypeTransactionViewSet,
    CategoryTransactionViewSet,
)

# ── Routers ───────────────────────────────────────────────────

transactions_router = DefaultRouter()
transactions_router.register(
    r'transactions',
    FinancialTransactionViewSet,
    basename='finance-transactions'
)

types_router = DefaultRouter()
types_router.register(
    r'types',
    TypeTransactionViewSet,
    basename='finance-types'
)

categories_router = DefaultRouter()
categories_router.register(
    r'categories',
    CategoryTransactionViewSet,
    basename='finance-categories'
)

"""
URLs resultantes bajo /api/admin/finance/:

  GET    /api/admin/finance/summary/

  GET    /api/admin/finance/types/
  POST   /api/admin/finance/types/
  GET    /api/admin/finance/types/{id}/
  PATCH  /api/admin/finance/types/{id}/
  DELETE /api/admin/finance/types/{id}/

  GET    /api/admin/finance/categories/
  POST   /api/admin/finance/categories/
  GET    /api/admin/finance/categories/{id}/
  PATCH  /api/admin/finance/categories/{id}/
  DELETE /api/admin/finance/categories/{id}/

  GET    /api/admin/finance/transactions/
  POST   /api/admin/finance/transactions/
  GET    /api/admin/finance/transactions/{id}/
  PATCH  /api/admin/finance/transactions/{id}/
  DELETE /api/admin/finance/transactions/{id}/

IMPORTANTE: 'summary/' va ANTES de los routers para que no sea
interceptada como si fuera un {id}.
"""

urlpatterns = [
    # Ruta fija — SIEMPRE antes de los routers
    path('summary/', FinanceSummaryView.as_view(), name='finance-summary'),

    # Routers CRUD — al final
    path('', include(types_router.urls)),
    path('', include(categories_router.urls)),
    path('', include(transactions_router.urls)),
]