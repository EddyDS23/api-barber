from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from utils.permissions import AllowAny
from .models import Appointment
from .serializers import AvailabilitySerializer, AppointmentBookingSerializer, AppointmentStatusSerializer
from .availability import get_available_slots
from .tasks import send_confirmation_email



class AvailabilityView(APIView):
    """
    GET /api/public/appointments/availability/
    Consulta slots disponibles para una fecha y servicios dados.
    """
    permission_classes = [AllowAny]
    @extend_schema(
        tags=['Public - Appointments'],
        summary='Consultar disponibilidad',
        description='''
            Retorna los horarios disponibles para una fecha y servicios dados.
            Si se especifica barber_id, filtra por ese barbero.
            Si no, muestra slots donde al menos un barbero está disponible.
        ''',
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        parameters=[
            OpenApiParameter(
                name='date',
                description='Fecha de la cita (YYYY-MM-DD)',
                required=True,
                type=str
            ),
            OpenApiParameter(
                name='service_ids',
                description='IDs de servicios separados por coma. Ejemplo: 1,2',
                required=True,
                type=str
            ),
            OpenApiParameter(
                name='barber_id',
                description='ID del barbero (opcional)',
                required=False,
                type=int
            ),
        ]
    )
    def get(self,request):
        # Parsear parámetros
        date_str = request.query_params.get('date')
        service_ids_str = request.query_params.get('service_ids', '')
        barber_id = request.query_params.get('barber_id')

        if not date_str or not service_ids_str:
            return Response(
                {'error': 'Los parámetros date y service_ids son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            service_ids = [int(id) for id in service_ids_str.split(',') if id.strip()]
            barber_id = int(barber_id) if barber_id else None
        except ValueError:
            return Response(
                {'error': 'Formato de parámetros inválido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar con serializer
        serializer = AvailabilitySerializer(data={
            'date': date,
            'service_ids': service_ids,
            'barber_id': barber_id
        })

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Obtener slots disponibles
        result = get_available_slots(date, service_ids, barber_id)
        return Response(result, status=status.HTTP_200_OK)


class BookAppointmentView(APIView):
    """
    POST /api/public/appointments/book/
    Agenda una nueva cita.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Public - Appointments'],
        summary='Agendar una cita',
        description='''
            Crea una nueva cita. Si el cliente no existe (por teléfono),
            se crea automáticamente. Si no se especifica barbero,
            se asigna automáticamente el menos ocupado del día.
        ''',
        request=AppointmentBookingSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        serializer = AppointmentBookingSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment = serializer.save()

        if appointment.client.email:
            send_confirmation_email.delay(appointment.id)


        # Construir respuesta con datos de la cita creada
        return Response({
            'success': True,
            'confirmation_code': appointment.confirmation_code,
            'appointment': {
                'id': appointment.id,
                'barber': appointment.barber.name,
                'date': str(appointment.date),
                'time': str(appointment.time),
                'services': [
                    {
                        'name': ap_service.service.name,
                        'price': str(ap_service.price_snapshot),
                        'duration': ap_service.duration_snapshot
                    }
                    for ap_service in appointment.appointmentservice_set.all()
                ],
                'total_amount': str(appointment.total_amount),
                'total_duration': appointment.total_duration,
                'notes': appointment.notes,
            }
        }, status=status.HTTP_201_CREATED)
    
class AppointmentStatusView(APIView):
    """
    GET /api/public/appointments/status/?code=ABC12345
    Permite al cliente consultar el estado de su cita
    usando su código de confirmación.
    No requiere autenticación.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Public - Appointments'],
        summary='Consultar estado de una cita',
        description='''
            El cliente ingresa su código de confirmación
            y recibe el estado actual de su cita.
            No requiere autenticación.
        ''',
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        parameters=[
            OpenApiParameter(
                name='code',
                description='Código de confirmación recibido al agendar. Ejemplo: ABC12345',
                required=True,
                type=str
            )
        ]
    )
    def get(self, request):
        code = request.query_params.get('code')

        if not code:
            return Response(
                {'error': 'El código de confirmación es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            appointment = Appointment.objects.select_related(
                'barber', 'status'
            ).prefetch_related(
                'appointmentservice_set__service'
            ).get(confirmation_code=code.upper())

        except Appointment.DoesNotExist:
            return Response(
                {'error': 'No se encontró ninguna cita con ese código.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AppointmentStatusSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)


