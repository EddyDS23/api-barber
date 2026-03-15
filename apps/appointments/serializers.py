import random 
import string
from rest_framework import serializers
from apps.clients.models import Client
from apps.services.models import Service
from apps.barbers.models import Barber
from .models import Appointment, AppointmentService, StatusAppointment
from .availability import get_available_slots, is_slot_available


class ClientBookingSerializer(serializers.Serializer):
    """
    Datos del cliente al momento de agendar.
    Si el teléfono ya existe en la BD, se reutiliza el cliente.
    Si no existe, se crea uno nuevo.
    """
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)


class AvailabilitySerializer(serializers.Serializer):
    """
    Serializer para consultar disponibilidad.
    GET /api/public/appointments/availability/
    """
    date = serializers.DateField()
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    barber_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_service_ids(self, value):
        services = Service.objects.filter(id__in=value, is_active=True)
        if services.count() != len(value):
            raise serializers.ValidationError(
                'Uno o más servicios no son válidos o están inactivos.'
            )
        return value

    def validate_barber_id(self, value):
        if value:
            if not Barber.objects.filter(id=value, status__name='Activo').exists():
                raise serializers.ValidationError(
                    'El barbero no existe o no está activo.'
                )
        return value


class AppointmentBookingSerializer(serializers.Serializer):
    """
    Serializer para agendar una cita.
    POST /api/public/appointments/book/
    """
    client = ClientBookingSerializer()
    date = serializers.DateField()
    # Acepta múltiples formatos de tiempo incluyendo el ISO de Swagger
    time = serializers.TimeField(
        input_formats=['%H:%M', '%H:%M:%S', '%H:%M:%S.%fZ', 'iso-8601']
    )
    service_ids = serializers.ListField(  # ← corregido (era services_ids)
        child=serializers.IntegerField(),
        min_length=1
    )
    barber_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_service_ids(self, value):
        services = Service.objects.filter(id__in=value, is_active=True)
        if services.count() != len(value):
            raise serializers.ValidationError(
                'Uno o más servicios no son válidos o están inactivos.'
            )
        return value

    def validate(self, attrs):
        service_ids = attrs.get('service_ids', [])

        if not service_ids:
            raise serializers.ValidationError(
                'Debe seleccionar al menos un servicio.'
            )

        services = Service.objects.filter(id__in=service_ids)
        total_duration = sum(s.duration for s in services)

        available = is_slot_available(
            attrs['date'],
            attrs['time'],
            total_duration,
            attrs.get('barber_id')
        )

        if not available:
            raise serializers.ValidationError(
                'El horario seleccionado no está disponible.'
            )

        return attrs

    def generate_confirmation_code(self):
        """Genera un código único de 8 caracteres alfanuméricos."""
        while True:
            code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            if not Appointment.objects.filter(confirmation_code=code).exists():
                return code

    def create(self, validated_data):
        from .auto_assign import auto_assign_barber  # ← corregido (era auto_assing)

        client_data = validated_data.pop('client')
        service_ids = validated_data.pop('service_ids')  # ← corregido
        barber_id = validated_data.pop('barber_id', None)
        notes = validated_data.pop('notes', '')

        # 1. Buscar o crear cliente por teléfono
        client, created = Client.objects.get_or_create(
            phone=client_data['phone'],
            defaults={
                'full_name': client_data['full_name'],
                'email': client_data.get('email', None)
            }
        )

        # 2. Obtener servicios y calcular totales
        services = Service.objects.filter(id__in=service_ids)
        total_amount = sum(s.price for s in services)
        total_duration = sum(s.duration for s in services)

        # 3. Asignar barbero (manual o automático)
        if barber_id:
            barber = Barber.objects.get(id=barber_id)
        else:
            barber = auto_assign_barber(
                validated_data['date'],
                validated_data['time'],
                total_duration
            )
            if not barber:
                raise serializers.ValidationError(
                    'No hay barberos disponibles para este horario.'
                )

        # 4. Obtener status "Confirmada"
        status = StatusAppointment.objects.get(name='Confirmada')

        # 5. Crear la cita
        appointment = Appointment.objects.create(
            client=client,
            barber=barber,
            status=status,
            date=validated_data['date'],
            time=validated_data['time'],
            notes=notes,
            total_amount=total_amount,
            total_duration=total_duration,
            confirmation_code=self.generate_confirmation_code()
        )

        # 6. Crear AppointmentService con snapshots
        for service in services:
            AppointmentService.objects.create(
                appointment=appointment,
                service=service,
                price_snapshot=service.price,
                duration_snapshot=service.duration
            )

        return appointment
    

class AppointmentStatusSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para consulta pública de cita.
    El cliente solo puede ver información básica de su cita,
    no datos sensibles como notas internas.
    """
    barber_name = serializers.CharField(source='barber.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    services = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'confirmation_code',
            'date',
            'time',
            'barber_name',
            'status_name',
            'services',
            'total_amount',
            'total_duration',
        ]

    def get_services(self, obj):
        return [
            {
                'name': ap_service.service.name,
                'price': str(ap_service.price_snapshot),
                'duration': ap_service.duration_snapshot,
            }
            for ap_service in obj.appointmentservice_set.all()
        ]