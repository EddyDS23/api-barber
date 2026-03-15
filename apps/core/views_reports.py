# apps/core/views_reports.py

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from backend.utils.permissions import IsAdmin
from apps.appointments.models import Appointment, AppointmentService
from apps.barbers.models import Barber
from apps.finance.models import FinancialTransaction, TypeTransaction
from apps.core.views_dashboard import get_month_ranges

REPORTS_TAG = 'Admin - Reports'

# Nombres de días en español (Python: 0=Lunes … 6=Domingo)
DAY_NAMES = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 1: /api/admin/reports/income-chart/
# ═════════════════════════════════════════════════════════════

@extend_schema(
    tags=[REPORTS_TAG],
    summary='Gráfica de ingresos',
    parameters=[
        OpenApiParameter(
            name='period',
            description=(
                'today = ingresos por hora del día actual\n'
                'week  = ingresos por día (últimos 7 días)\n'
                'month = ingresos por día del mes actual\n'
                'year  = ingresos por mes del año actual'
            ),
            required=False,
            type=str,
            enum=['today', 'week', 'month', 'year'],
        )
    ]
)
class ReportIncomeChartView(APIView):
    """
    GET /api/admin/reports/income-chart/?period=today|week|month|year

    period=today  → eje X = horas del día actual        (00:00 - 23:00)
    period=week   → eje X = últimos 7 días              (Lun, Mar...)
    period=month  → eje X = días del mes actual         (1, 2, 3... 30/31)
    period=year   → eje X = meses del año actual        (Ene, Feb... Dic)

    Fuente: financial_transactions WHERE type='Ingreso' AND amount > 0
    """
    permission_classes = [IsAdmin]

    MONTH_NAMES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                   'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    def get(self, request):
        period = request.query_params.get('period', 'week')

        try:
            ingreso_type = TypeTransaction.objects.get(name='Ingreso')
        except TypeTransaction.DoesNotExist:
            ingreso_type = None

        if period == 'today':
            return self._income_by_hour(ingreso_type)
        elif period == 'month':
            return self._income_by_day_of_month(ingreso_type)
        elif period == 'year':
            return self._income_by_month_of_year(ingreso_type)
        else:
            return self._income_by_week(ingreso_type)

    def _income_by_hour(self, ingreso_type):
        """Ingresos del día de hoy agrupados por hora (00:00 - 23:00)."""
        today = date.today()

        transactions = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date=today,
            amount__gt=0
        ).values('created_at__hour').annotate(total=Sum('amount'))

        income_by_hour = {row['created_at__hour']: row['total'] for row in transactions}

        data = []
        for hour in range(24):
            data.append({
                'label':  f'{hour:02d}:00',
                'income': income_by_hour.get(hour, Decimal('0'))
            })

        return Response({
            'period': 'today',
            'label':  'Ingresos de hoy por hora',
            'data':   data
        })

    def _income_by_week(self, ingreso_type):
        """Ingresos de los últimos 7 días agrupados por día."""
        today      = date.today()
        week_start = today - timedelta(days=6)

        transactions = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(week_start, today),
            amount__gt=0
        ).values('date').annotate(total=Sum('amount'))

        income_by_date = {row['date']: row['total'] for row in transactions}

        data = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            data.append({
                'label':  DAY_NAMES[day.weekday()],
                'date':   day.isoformat(),
                'income': income_by_date.get(day, Decimal('0'))
            })

        return Response({
            'period': 'week',
            'label':  'Ingresos de la semana por día',
            'data':   data
        })

    def _income_by_day_of_month(self, ingreso_type):
        """
        Ingresos del mes actual agrupados por día (1, 2, 3... 30/31).
        Cada punto del eje X es un día del mes.
        """
        today         = date.today()
        month_start   = today.replace(day=1)

        # Último día del mes
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        transactions = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(month_start, month_end),
            amount__gt=0
        ).values('date').annotate(total=Sum('amount'))

        income_by_date = {row['date']: row['total'] for row in transactions}

        data = []
        total_days = (month_end - month_start).days + 1
        for i in range(total_days):
            day = month_start + timedelta(days=i)
            data.append({
                'label':  str(day.day),       # "1", "2", ... "31"
                'date':   day.isoformat(),
                'income': income_by_date.get(day, Decimal('0'))
            })

        return Response({
            'period': 'month',
            'label':  f'Ingresos de {self.MONTH_NAMES[today.month - 1]} {today.year}',
            'data':   data
        })

    def _income_by_month_of_year(self, ingreso_type):
        """
        Ingresos del año actual agrupados por mes (Ene, Feb... Dic).
        Cada punto del eje X es un mes.
        Solo muestra hasta el mes actual (los futuros retornan 0).
        """
        today      = date.today()
        year_start = today.replace(month=1, day=1)
        year_end   = today.replace(month=12, day=31)

        transactions = FinancialTransaction.objects.filter(
            type=ingreso_type,
            date__range=(year_start, year_end),
            amount__gt=0
        ).values('date__month').annotate(total=Sum('amount'))

        # dict {mes_numero: total} → {1: 1200.00, 2: 980.00, ...}
        income_by_month = {row['date__month']: row['total'] for row in transactions}

        data = []
        for month_num in range(1, 13):
            data.append({
                'label':  self.MONTH_NAMES[month_num - 1],   # "Ene", "Feb"...
                'month':  month_num,
                'income': income_by_month.get(month_num, Decimal('0')),
                # Los meses futuros se marcan para que el frontend los maneje
                'is_future': month_num > today.month
            })

        return Response({
            'period': 'year',
            'label':  f'Ingresos del año {today.year}',
            'data':   data
        })


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 2: /api/admin/reports/top-services/
# ═════════════════════════════════════════════════════════════

@extend_schema(
    tags=[REPORTS_TAG],
    summary='Top 3 servicios más solicitados del mes'
)
class ReportTopServicesView(APIView):
    """
    GET /api/admin/reports/top-services/

    Retorna los TOP 3 servicios más solicitados del mes actual.
    Solo cuenta citas con status 'Completada'.
    Los porcentajes se calculan sobre el total de los TOP 3 (no del total general).

    Fuente: appointments_services JOIN appointments (status=Completada)
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        first_current, last_current, _, _ = get_month_ranges()

        # Anotamos cada servicio con el count de veces que aparece
        # en citas completadas del mes actual
        top_services = (
            AppointmentService.objects
            .filter(
                appointment__date__range=(first_current, last_current),
                appointment__status__name='Completada'
            )
            .values('service__id', 'service__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:3]  # Solo TOP 3
        )

        services_list = list(top_services)

        # Total de los TOP 3 para calcular porcentajes
        total = sum(s['count'] for s in services_list)

        data = []
        for rank, service in enumerate(services_list, start=1):
            percent = int(round((service['count'] / total) * 100)) if total > 0 else 0
            data.append({
                'rank':    rank,
                'id':      service['service__id'],
                'name':    service['service__name'],
                'count':   service['count'],
                'percent': percent
            })

        return Response({
            'period': 'month',
            'services': data
        })


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 3: /api/admin/reports/top-barbers/
# ═════════════════════════════════════════════════════════════

@extend_schema(
    tags=[REPORTS_TAG],
    summary='Top 3 barberos con más citas completadas del mes'
)
class ReportTopBarbersView(APIView):
    """
    GET /api/admin/reports/top-barbers/

    Retorna los TOP 3 barberos con más citas completadas del mes actual.
    Usado para las barras horizontales de rendimiento.

    Fuente: barbers JOIN appointments (status=Completada)
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        first_current, last_current, _, _ = get_month_ranges()

        top_barbers = (
            Barber.objects
            .filter(
                appointments__date__range=(first_current, last_current),
                appointments__status__name='Completada'
            )
            .annotate(appointments_count=Count('appointments'))
            .order_by('-appointments_count')[:3]
        )

        data = []
        for rank, barber in enumerate(top_barbers, start=1):
            data.append({
                'rank':               rank,
                'id':                 barber.id,
                'name':               barber.name,
                'appointments_count': barber.appointments_count,
                'color_code':         barber.color_code  # para colorear la barra
            })

        return Response({
            'period': 'month',
            'barbers': data
        })


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 4: /api/admin/reports/occupancy-heatmap/
# ═════════════════════════════════════════════════════════════

@extend_schema(
    tags=[REPORTS_TAG],
    summary='Heatmap de ocupación por día y hora del mes actual'
)
class ReportOccupancyHeatmapView(APIView):
    """
    GET /api/admin/reports/occupancy-heatmap/

    Retorna el promedio de citas por franja horaria y día de la semana
    para el mes actual. Útil para identificar horas pico.

    Lógica:
      1. Traemos todas las citas del mes (estados activos)
      2. Agrupamos por día de la semana (0=Dom…6=Sáb en DB) y hora
      3. Calculamos cuántas semanas tiene el mes para promediar
      4. is_peak = True si count >= peak_threshold (default: 4)

    Response:
    {
      "days":  ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"],
      "hours": ["09:00", "10:00", ...],
      "data":  [{"day": "Lun", "hour": "09:00", "count": 2, "is_peak": false}, ...],
      "peak_threshold": 4
    }
    """
    permission_classes = [IsAdmin]
    PEAK_THRESHOLD = 4

    # Días que mostramos (Lun-Sáb, excluimos Domingo)
    # En el schema la DB usa: 0=Domingo, 1=Lunes ... 6=Sábado
    # Mapeamos a nombres en español
    DB_DAY_MAP = {1: 'Lun', 2: 'Mar', 3: 'Mié', 4: 'Jue', 5: 'Vie', 6: 'Sáb'}

    def get(self, request):
        first_current, last_current, _, _ = get_month_ranges()

        active_statuses = ['Pendiente', 'Confirmada', 'En progreso', 'Completada']

        # Traemos todas las citas del mes con su hora y día
        # extra('day_of_week') extrae el día de la semana de la fecha en PostgreSQL
        # (0=Dom, 1=Lun, ..., 6=Sáb — igual que el schema)
        appointments = (
            Appointment.objects
            .filter(
                date__range=(first_current, last_current),
                status__name__in=active_statuses
            )
            .extra(select={'day_of_week': 'EXTRACT(DOW FROM date)'})
            .values('day_of_week', 'time__hour')
            .annotate(count=Count('id'))
        )

        # Calculamos cuántas semanas tiene el mes para promediar los conteos
        # Esto evita que un mes con 5 lunes parezca más ocupado que uno con 4
        total_days = (last_current - first_current).days + 1
        weeks_in_month = total_days / 7

        # Construimos lookup {(day_of_week, hour): avg_count}
        heatmap_data = {}
        for row in appointments:
            dow  = int(row['day_of_week'])
            hour = row['time__hour']
            avg  = round(row['count'] / weeks_in_month, 1)
            heatmap_data[(dow, hour)] = avg

        # Horas de operación — usamos rango fijo 9-18
        # Idealmente vendría de BusinessSettings.time_slot_duration
        hours = [f'{h:02d}:00' for h in range(9, 19)]

        # Construimos la matriz de datos
        data = []
        for dow, day_name in self.DB_DAY_MAP.items():
            for hour_str in hours:
                hour_int = int(hour_str.split(':')[0])
                count = heatmap_data.get((dow, hour_int), 0)
                data.append({
                    'day':     day_name,
                    'hour':    hour_str,
                    'count':   count,
                    'is_peak': count >= self.PEAK_THRESHOLD
                })

        return Response({
            'days':           list(self.DB_DAY_MAP.values()),
            'hours':          hours,
            'data':           data,
            'peak_threshold': self.PEAK_THRESHOLD
        })