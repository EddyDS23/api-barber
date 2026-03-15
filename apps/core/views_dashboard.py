# apps/core/views_dashboard.py

from datetime import date, datetime
from decimal import Decimal

from django.db.models import Sum, Count, Q
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from backend.utils.permissions import IsAdmin
from apps.appointments.models import Appointment, StatusAppointment
from apps.finance.models import FinancialTransaction, TypeTransaction
from apps.barbers.models import Barber

from apps.core.utils import calc_percent_change, get_month_ranges


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 1: /api/admin/dashboard/stats/
# ═════════════════════════════════════════════════════════════
class DashboardStatsView(APIView):
    """
    GET /api/admin/dashboard/stats/

    Retorna los 4 KPI cards del panel:
      1. total_income_month    → ingresos del mes actual + % vs anterior
      2. appointments_today    → citas activas de hoy
      3. cancellations_month   → cancelaciones + no-show del mes
      4. top_barber            → barbero con más citas completadas este mes
    """
    permission_classes = [IsAdmin]

    @extend_schema(tags=['Admin - Dashboard'])
    def get(self, request):
        today = date.today()
        first_current, last_current, first_previous, last_previous = get_month_ranges()

        # ── 1. INGRESOS DEL MES ──────────────────────────────
        # Buscamos la FK del tipo "Ingreso" para no depender de strings en cada query
        try:
            ingreso_type = TypeTransaction.objects.get(name='Ingreso')
        except TypeTransaction.DoesNotExist:
            ingreso_type = None

        # Suma de transacciones de tipo Ingreso en el mes actual
        income_current = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(first_current, last_current)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Suma del mes anterior para calcular la variación
        income_previous = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(first_previous, last_previous)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        income_percent = calc_percent_change(income_current, income_previous)

        # ── 2. CITAS DE HOY ──────────────────────────────────
        # Contamos citas de hoy con estados "activos" (excluimos canceladas/no-show)
        # Q() permite combinar condiciones OR en Django ORM
        active_statuses = ['Pendiente', 'Confirmada', 'En progreso', 'Completada']
        appointments_today = Appointment.objects.filter(
            date=today,
            status__name__in=active_statuses
        ).count()

        # ── 3. CANCELACIONES DEL MES ─────────────────────────
        # Incluimos tanto "Cancelada" como "No asistió"
        cancellations_month = Appointment.objects.filter(
            date__range=(first_current, last_current),
            status__name__in=['Cancelada', 'No asistió']
        ).count()

        # ── 4. BARBERO TOP ───────────────────────────────────
        # Anotamos cada barbero con el conteo de citas "Completada" del mes
        # y ordenamos descendente → el primero es el top
        top_barber_qs = (
            Barber.objects
            .filter(
                appointments__date__range=(first_current, last_current),
                appointments__status__name='Completada'
            )
            .annotate(completed_count=Count('appointments'))
            .order_by('-completed_count')
            .first()
        )

        top_barber = None
        if top_barber_qs:
            top_barber = {
                'name': top_barber_qs.name,
                'appointments_count': top_barber_qs.completed_count
            }

        # ── RESPONSE ─────────────────────────────────────────
        return Response({
            'total_income_month': {
                'value': income_current,
                'percent_change': income_percent,
                # True si subió, False si bajó/igual → el frontend colorea el badge
                'is_positive': income_percent >= 0
            },
            'appointments_today': appointments_today,
            'cancellations_month': cancellations_month,
            'top_barber': top_barber  # puede ser null si no hay datos
        })


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 2: /api/admin/dashboard/weekly-performance/
# ═════════════════════════════════════════════════════════════
class DashboardWeeklyPerformanceView(APIView):
    """
    GET /api/admin/dashboard/weekly-performance/

    Retorna ingresos agrupados día a día para los últimos 7 días,
    el total de la semana y la comparación con la semana anterior.

    Ejemplo de response:
    {
      "week_total": 3450.00,
      "vs_last_week_percent": 8,
      "days": [
        {"date": "2024-06-10", "day": "Lun", "income": 450.00},
        ...
      ]
    }
    """
    permission_classes = [IsAdmin]

    # Mapa de weekday de Python → nombre en español
    # Python: 0=Lunes, 1=Martes, ... 6=Domingo
    DAY_NAMES = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    @extend_schema(tags=['Admin - Dashboard'])
    def get(self, request):
        from datetime import timedelta

        today = date.today()

        # Rango semana actual: últimos 7 días (incluyendo hoy)
        week_start = today - timedelta(days=6)

        # Rango semana anterior: los 7 días antes de la semana actual
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = week_start - timedelta(days=1)

        # Tipo Ingreso
        try:
            ingreso_type = TypeTransaction.objects.get(name='Ingreso')
        except TypeTransaction.DoesNotExist:
            ingreso_type = None

        # ── SEMANA ACTUAL: query agrupada por fecha ───────────
        # values('date') agrupa los registros por fecha
        # annotate(total=Sum('amount')) suma los montos de cada grupo
        week_qs = (
            FinancialTransaction.objects
            .filter(type=ingreso_type, date__range=(week_start, today))
            .values('date')
            .annotate(total=Sum('amount'))
        )

        # Convertimos el QuerySet a un dict {date: total} para lookup rápido
        income_by_date = {row['date']: row['total'] for row in week_qs}

        # Construimos la lista de 7 días, rellenando con 0 los días sin ingresos
        days = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            days.append({
                'date': day.isoformat(),               # "2024-06-10"
                'day': self.DAY_NAMES[day.weekday()],  # "Lun"
                'income': income_by_date.get(day, Decimal('0'))
            })

        week_total = sum(d['income'] for d in days)

        # ── SEMANA ANTERIOR: solo necesitamos el total ────────
        prev_week_total = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(prev_week_start, prev_week_end)
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        vs_last_week = calc_percent_change(week_total, prev_week_total)

        return Response({
            'week_total': week_total,
            'vs_last_week_percent': vs_last_week,
            'is_positive': vs_last_week >= 0,
            'days': days
        })


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 3: /api/admin/dashboard/upcoming-appointments/
# ═════════════════════════════════════════════════════════════
class DashboardUpcomingAppointmentsView(APIView):
    """
    GET /api/admin/dashboard/upcoming-appointments/?limit=5

    Retorna las próximas citas del día de hoy que aún no han pasado.

    Filtros aplicados:
      - date = hoy
      - time >= hora actual (solo las que vienen)
      - status en [Pendiente, Confirmada, En progreso]
      - ordenadas por time ASC (las más próximas primero)
      - limit: query param, default 5, max 20
    """
    permission_classes = [IsAdmin]

    @extend_schema(tags=['Admin - Dashboard'])
    def get(self, request):
        try:
            limit = min(int(request.query_params.get('limit', 4)), 4)
        except (ValueError, TypeError):
            limit = 4

        today = date.today()
        now_time = timezone.localtime().time()

        all_statuses = [
            'Pendiente', 'Confirmada', 'En progreso',
            'Completada', 'Cancelada', 'No asistió'
        ]

        appointments = (
            Appointment.objects
            .filter(
                date=today,
                time__gte=now_time,
                status__name__in=all_statuses
            )
            .select_related('client', 'barber', 'status')
            .prefetch_related('appointmentservice_set__service')
            .order_by('time')[:limit]
        )

        data = []
        for appt in appointments:
            services = [
                ap_srv.service.name
                for ap_srv in appt.appointmentservice_set.all()
            ]

            data.append({
                'id': appt.id,
                'time': appt.time.strftime('%H:%M'),
                'client': appt.client.full_name,
                'services': services,
                'barber': appt.barber.name,
                'status': appt.status.name,
                'confirmation_code': appt.confirmation_code
            })

        return Response(data)