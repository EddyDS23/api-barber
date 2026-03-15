# apps/appointments/views_admin.py

from datetime import date, datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from backend.utils.permissions import IsAdmin
from apps.barbers.models import Barber
from apps.core.models import BusinessSettings, BusinessHours
from .models import Appointment, StatusAppointment
from .serializers_admin import (
    AppointmentDetailSerializer,
    ChangeStatusSerializer,
    QuickAppointmentSerializer,
)

AGENDA_TAG = 'Admin - Agenda'


# ─────────────────────────────────────────────────────────────
#  HELPER: generar slots del día según horario del negocio
# ─────────────────────────────────────────────────────────────

def get_day_slots(target_date: date) -> list:
    """
    Genera la lista de slots horarios para un día dado,
    basándose en el horario configurado en BusinessHours.

    Conversión de weekday:
      Python: 0=Lunes ... 6=Domingo
      DB:     0=Domingo, 1=Lunes ... 6=Sábado

    Retorna lista de strings: ['09:00', '09:30', '10:00', ...]
    Si el día no es laborable retorna lista vacía.
    """
    # Convertir weekday de Python a formato del schema de DB
    python_weekday = target_date.weekday()
    if python_weekday == 6:   # Domingo en Python
        db_day = 0
    else:
        db_day = python_weekday + 1

    try:
        hours = BusinessHours.objects.get(day_of_week=db_day)
    except BusinessHours.DoesNotExist:
        return []

    if not hours.is_working or not hours.opening_time or not hours.closing_time:
        return []

    # Duración de cada slot desde BusinessSettings
    try:
        settings       = BusinessSettings.objects.get(id=1)
        slot_duration  = settings.time_slot_duration or 30
    except BusinessSettings.DoesNotExist:
        slot_duration = 30

    slots   = []
    current = datetime.combine(target_date, hours.opening_time)
    closing = datetime.combine(target_date, hours.closing_time)

    while current < closing:
        slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=slot_duration)

    return slots


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 1: GET /api/admin/agenda/schedule/?date=YYYY-MM-DD
# ═════════════════════════════════════════════════════════════

@extend_schema(
    tags=[AGENDA_TAG],
    summary='Matriz de agenda del día',
    parameters=[
        OpenApiParameter(
            name='date',
            description='Fecha a consultar en formato YYYY-MM-DD. Default: hoy.',
            required=False,
            type=str,
        )
    ]
)
class AgendaScheduleView(APIView):
    """
    GET /api/admin/agenda/schedule/?date=YYYY-MM-DD

    Retorna la matriz completa del calendario para el día solicitado:
      - Columnas: barberos activos
      - Filas:    slots horarios según BusinessHours
      - Celdas:   cita asignada o null (slot vacío)

    Response:
    {
      "date": "2024-02-15",
      "is_working_day": true,
      "slots": ["09:00", "09:30", ...],
      "barbers": [
        {
          "id": 1,
          "name": "Marcus Titan",
          "color_code": "#FF5733",
          "slots": [
            {"time": "09:00", "appointment": null},
            {"time": "09:30", "appointment": {
              "id": 45,
              "client": "Juan Pérez",
              "services": ["Corte Clásico"],
              "status": "Confirmada",
              "total_amount": "15.00",
              "confirmation_code": "ABC12345"
            }}
          ]
        }
      ]
    }
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        # Parsear fecha del query param, default = hoy
        date_str = request.query_params.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = date.today()

        # Generar slots del día
        slots = get_day_slots(target_date)
        is_working_day = len(slots) > 0

        # Barberos activos ordenados por nombre
        barbers = Barber.objects.filter(
            status__name='Activo'
        ).order_by('name')

        # Traer TODAS las citas del día en una sola query
        # Luego las distribuimos en memoria (más eficiente que N queries)
        appointments = (
            Appointment.objects
            .filter(date=target_date)
            .select_related('client', 'status')
            .prefetch_related('appointmentservice_set__service')
        )

        # Construimos lookup {(barber_id, 'HH:MM'): appointment}
        appt_lookup = {}
        for appt in appointments:
            key = (appt.barber_id, appt.time.strftime('%H:%M'))
            appt_lookup[key] = appt

        # Construir la respuesta
        barbers_data = []
        for barber in barbers:
            barber_slots = []
            for slot_time in slots:
                appt = appt_lookup.get((barber.id, slot_time))

                if appt:
                    services = [
                        ap_srv.service.name
                        for ap_srv in appt.appointmentservice_set.all()
                    ]
                    appt_data = {
                        'id':                appt.id,
                        'client':            appt.client.full_name,
                        'client_phone':      appt.client.phone,
                        'services':          services,
                        'status':            appt.status.name,
                        'total_amount':      str(appt.total_amount),
                        'total_duration':    appt.total_duration,
                        'confirmation_code': appt.confirmation_code,
                        'notes':             appt.notes or '',
                    }
                else:
                    appt_data = None

                barber_slots.append({
                    'time':        slot_time,
                    'appointment': appt_data,
                })

            barbers_data.append({
                'id':         barber.id,
                'name':       barber.name,
                'color_code': barber.color_code,
                'slots':      barber_slots,
            })

        return Response({
            'date':           target_date.isoformat(),
            'is_working_day': is_working_day,
            'slots':          slots,
            'barbers':        barbers_data,
        })


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 2: GET /api/admin/agenda/appointments/{id}/
# ═════════════════════════════════════════════════════════════

@extend_schema(tags=[AGENDA_TAG], summary='Detalle de cita')
class AgendaAppointmentDetailView(APIView):
    """
    GET /api/admin/agenda/appointments/{id}/

    Retorna el detalle completo de una cita para el modal
    de "Ver/Editar Estado" de la Agenda.
    """
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            appointment = (
                Appointment.objects
                .select_related('client', 'barber', 'status')
                .prefetch_related('appointmentservice_set__service')
                .get(pk=pk)
            )
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Cita no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AppointmentDetailSerializer(appointment)
        return Response(serializer.data)


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 3: PATCH /api/admin/agenda/appointments/{id}/change-status/
# ═════════════════════════════════════════════════════════════

@extend_schema(tags=[AGENDA_TAG], summary='Cambiar estado de una cita',request=ChangeStatusSerializer)
class AgendaChangeStatusView(APIView):
    """
    PATCH /api/admin/agenda/appointments/{id}/change-status/
    Body: {"status": "Completada"}

    Estados válidos:
      Pendiente | Confirmada | En progreso | Completada | Cancelada | No asistió
    """
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.select_related('status').get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Cita no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChangeStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = StatusAppointment.objects.get(
            id=serializer.validated_data['status_id']
        )

        old_status = appointment.status.name
        appointment.status = new_status
        appointment.save()

        return Response({
            'message':    'Estado actualizado correctamente.',
            'id':         appointment.id,
            'old_status': old_status,
            'new_status': new_status.name,
        })


# ═════════════════════════════════════════════════════════════
#  ENDPOINT 4: POST /api/admin/agenda/quick-appointment/
# ═════════════════════════════════════════════════════════════

@extend_schema(tags=[AGENDA_TAG], summary='Crear cita rápida desde la agenda',request=QuickAppointmentSerializer)
class AgendaQuickAppointmentView(APIView):
    """
    POST /api/admin/agenda/quick-appointment/

    Crea una cita desde el panel admin al hacer click en un slot vacío.

    Body:
    {
      "barber_id":    1,
      "date":         "2024-02-15",
      "time":         "10:00",
      "client_name":  "Juan Pérez",
      "client_phone": "555-1234",
      "service_ids":  [1, 2],
      "notes":        "Opcional"
    }
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = QuickAppointmentSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        appointment = serializer.save()

        return Response({
            'success':           True,
            'message':           'Cita creada correctamente.',
            'confirmation_code': appointment.confirmation_code,
            'appointment': {
                'id':            appointment.id,
                'client':        appointment.client.full_name,
                'barber':        appointment.barber.name,
                'date':          appointment.date,
                'time':          appointment.time.strftime('%H:%M'),
                'status':        appointment.status.name,
                'total_amount':  str(appointment.total_amount),
                'total_duration':appointment.total_duration,
            }
        }, status=status.HTTP_201_CREATED)