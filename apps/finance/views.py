# apps/finance/views.py

from decimal import Decimal

from django.db.models import Sum

from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiTypes

from utils.permissions import IsAdmin
from .models import FinancialTransaction, TypeTransaction, CategoryTransaction
from .serializers import (
    FinancialTransactionSerializer,
    TypeTransactionSerializer,
    CategoryTransactionSerializer,
)
from apps.core.utils import calc_percent_change, get_month_ranges

FINANCE_TAG = 'Admin - Finance'
FINANCE_CATEGORY_TAG = 'Admin - Category - Finance'
FINANCE_TYPE_TAG = 'Admin - Type - Finance'


# ═════════════════════════════════════════════════════════════
#  ENDPOINT: /api/admin/finance/summary/
# ═════════════════════════════════════════════════════════════

@extend_schema(tags=[FINANCE_TAG], summary='Resumen de finanzas',responses={200: OpenApiTypes.OBJECT})
class FinanceSummaryView(APIView):
    """
    GET /api/admin/finance/summary/

    Retorna las 3 cards de métricas del mes actual vs anterior:
      - income     → suma de transacciones con amount > 0 (ingresos)
      - expenses   → suma absoluta de transacciones con amount < 0 (egresos)
      - net_profit → ingresos - gastos

    IMPORTANTE sobre el schema de la DB:
      amount > 0 = ingreso
      amount < 0 = egreso
      La suma de egresos es negativa → usamos abs() para mostrarla positiva.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        first_current, last_current, first_previous, last_previous = get_month_ranges()

        try:
            ingreso_type = TypeTransaction.objects.get(name='Ingreso')
        except TypeTransaction.DoesNotExist:
            ingreso_type = None

        try:
            egreso_type = TypeTransaction.objects.get(name='Egreso')
        except TypeTransaction.DoesNotExist:
            egreso_type = None

        # ── INGRESOS (amount positivo) ────────────────────────
        income_current = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(first_current, last_current)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        income_previous = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(first_previous, last_previous)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # ── GASTOS (amount negativo en DB → abs() para mostrar positivo) ──
        expenses_current = abs(
            FinancialTransaction.objects.filter(
                type=egreso_type,
                date__range=(first_current, last_current)
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        )

        expenses_previous = abs(
            FinancialTransaction.objects.filter(
                type=egreso_type,
                date__range=(first_previous, last_previous)
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        )

        # ── UTILIDAD NETA ────────────────────────────────────
        net_current  = income_current  - expenses_current
        net_previous = income_previous - expenses_previous

        income_percent   = calc_percent_change(income_current,   income_previous)
        expenses_percent = calc_percent_change(expenses_current, expenses_previous)
        net_percent      = calc_percent_change(net_current,      net_previous)

        return Response({
            'income': {
                'current':        income_current,
                'previous':       income_previous,
                'percent_change': income_percent,
                'is_positive':    income_percent >= 0
            },
            'expenses': {
                'current':        expenses_current,
                'previous':       expenses_previous,
                # Gastos: is_positive = True cuando BAJARON (menos gasto = bueno)
                'percent_change': expenses_percent,
                'is_positive':    expenses_percent <= 0
            },
            'net_profit': {
                'current':        net_current,
                'previous':       net_previous,
                'percent_change': net_percent,
                'is_positive':    net_percent >= 0
            }
        })


# ═════════════════════════════════════════════════════════════
#  VIEWSET: /api/admin/finance/transactions/
# ═════════════════════════════════════════════════════════════

@extend_schema_view(
    list=extend_schema(
        tags=[FINANCE_TAG],
        summary='Listar transacciones',
        description=(
            'Filtros disponibles:\n'
            '?type=1 → por tipo (ID)\n'
            '?category=2 → por categoría (ID)\n'
            '?date=2024-06-15 → fecha exacta\n'
            '?date_from=2024-06-01&date_to=2024-06-30 → rango\n'
            '?search=concepto → búsqueda\n'
            '?ordering=-date → ordenamiento (default: -date)'
        )
    ),
    create=extend_schema(tags=[FINANCE_TAG],         summary='Crear transacción'),
    retrieve=extend_schema(tags=[FINANCE_TAG],       summary='Detalle de transacción'),
    partial_update=extend_schema(tags=[FINANCE_TAG], summary='Editar transacción'),
    destroy=extend_schema(tags=[FINANCE_TAG],        summary='Eliminar transacción'),
)
class FinancialTransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de transacciones financieras.

    GET    /api/admin/finance/transactions/
    POST   /api/admin/finance/transactions/
    GET    /api/admin/finance/transactions/{id}/
    PATCH  /api/admin/finance/transactions/{id}/
    DELETE /api/admin/finance/transactions/{id}/
    """
    permission_classes = [IsAdmin]
    serializer_class   = FinancialTransactionSerializer
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['concept']
    ordering_fields    = ['date', 'amount', 'concept']
    ordering           = ['-date']
    # Solo PATCH, no PUT
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = FinancialTransaction.objects.select_related(
            'type', 'category', 'appointment'
        ).all()

        type_id = self.request.query_params.get('type')
        if type_id:
            queryset = queryset.filter(type_id=type_id)

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        date_exact = self.request.query_params.get('date')
        if date_exact:
            queryset = queryset.filter(date=date_exact)

        date_from = self.request.query_params.get('date_from')
        date_to   = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {'message': 'Transacción eliminada correctamente.'},
            status=status.HTTP_200_OK
        )


# ═════════════════════════════════════════════════════════════
#  CRUD: /api/admin/finance/types/
# ═════════════════════════════════════════════════════════════

@extend_schema_view(
    list=extend_schema(tags=[FINANCE_TYPE_TAG],           summary='Listar tipos de transacción'),
    create=extend_schema(tags=[FINANCE_TYPE_TAG],         summary='Crear tipo de transacción'),
    retrieve=extend_schema(tags=[FINANCE_TYPE_TAG],       summary='Detalle de tipo'),
    partial_update=extend_schema(tags=[FINANCE_TYPE_TAG], summary='Editar tipo de transacción'),
    destroy=extend_schema(tags=[FINANCE_TYPE_TAG],        summary='Eliminar tipo de transacción'),
)
class TypeTransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD de tipos de transacción (Ingreso / Egreso).

    GET    /api/admin/finance/types/
    POST   /api/admin/finance/types/
    PATCH  /api/admin/finance/types/{id}/
    DELETE /api/admin/finance/types/{id}/
    """
    permission_classes = [IsAdmin]
    serializer_class   = TypeTransactionSerializer
    queryset           = TypeTransaction.objects.all()
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Protección: no eliminar si tiene transacciones asociadas
        if FinancialTransaction.objects.filter(type=instance).exists():
            return Response(
                {'error': 'No se puede eliminar un tipo que tiene transacciones asociadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(
            {'message': 'Tipo eliminado correctamente.'},
            status=status.HTTP_200_OK
        )


# ═════════════════════════════════════════════════════════════
#  CRUD: /api/admin/finance/categories/
# ═════════════════════════════════════════════════════════════

@extend_schema_view(
    list=extend_schema(tags=[FINANCE_CATEGORY_TAG],           summary='Listar categorías'),
    create=extend_schema(tags=[FINANCE_CATEGORY_TAG],         summary='Crear categoría'),
    retrieve=extend_schema(tags=[FINANCE_CATEGORY_TAG],       summary='Detalle de categoría'),
    partial_update=extend_schema(tags=[FINANCE_CATEGORY_TAG], summary='Editar categoría'),
    destroy=extend_schema(tags=[FINANCE_CATEGORY_TAG],        summary='Eliminar categoría'),
)
class CategoryTransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD de categorías de transacción.

    GET    /api/admin/finance/categories/
    POST   /api/admin/finance/categories/
    PATCH  /api/admin/finance/categories/{id}/
    DELETE /api/admin/finance/categories/{id}/
    """
    permission_classes = [IsAdmin]
    serializer_class   = CategoryTransactionSerializer
    queryset           = CategoryTransaction.objects.all()
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Protección: no eliminar si tiene transacciones asociadas
        if FinancialTransaction.objects.filter(category=instance).exists():
            return Response(
                {'error': 'No se puede eliminar una categoría que tiene transacciones asociadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return Response(
            {'message': 'Categoría eliminada correctamente.'},
            status=status.HTTP_200_OK
        )