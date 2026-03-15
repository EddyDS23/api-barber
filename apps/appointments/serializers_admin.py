# apps/appointments/serializers_admin.py

import random
import string

from rest_framework import serializers

from apps.clients.models import Client
from apps.barbers.models import Barber
from apps.services.models import Service
from .models import Appointment, AppointmentService, StatusAppointment


# ─────────────────────────────────────────────────────────────
#  Serializer de detalle de cita (GET /agenda/appointments/{id}/)
# ─────────────────────────────────────────────────────────────

class AppointmentServiceDetailSerializer(serializers.ModelSerializer):
    """Detalle de cada servicio dentro de una cita."""
    name     = serializers.CharField(source='service.name',     read_only=True)
    price    = serializers.DecimalField(
        source='price_snapshot', max_digits=10, decimal_places=2, read_only=True
    )
    duration = serializers.IntegerField(
        source='duration_snapshot', read_only=True
    )

    class Meta:
        model  = AppointmentService
        fields = ['id', 'name', 'price', 'duration']


class AppointmentDetailSerializer(serializers.ModelSerializer):
    client_name  = serializers.CharField(source='client.full_name', read_only=True)
    client_phone = serializers.CharField(source='client.phone',     read_only=True)
    barber_name  = serializers.CharField(source='barber.name',      read_only=True)
    barber_color = serializers.CharField(source='barber.color_code',read_only=True)
    
    status_id    = serializers.IntegerField(source='status.id',     read_only=True)
    status_name  = serializers.CharField(source='status.name',      read_only=True)
    
    services = AppointmentServiceDetailSerializer(
        source='appointmentservice_set', many=True, read_only=True
    )

    class Meta:
        model  = Appointment
        fields = [
            'id',
            'client_name',
            'client_phone',
            'barber_name',
            'barber_color',
            'date',
            'time',
            'status_id',    
            'status_name',
            'services',
            'total_amount',
            'total_duration',
            'notes',
            'confirmation_code',
        ]


# ─────────────────────────────────────────────────────────────
#  Serializer para cambio de estado
# ─────────────────────────────────────────────────────────────

class ChangeStatusSerializer(serializers.Serializer):
    """
    PATCH /agenda/appointments/{id}/change-status/
    Body: {"status_id": 2}
    """
    status_id = serializers.IntegerField()

    def validate_status_id(self, value):
        if not StatusAppointment.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'El status con id {value} no existe.'
            )
        return value


# ─────────────────────────────────────────────────────────────
#  Serializer para cita rápida
# ─────────────────────────────────────────────────────────────

class QuickAppointmentSerializer(serializers.Serializer):
    """
    POST /agenda/quick-appointment/

    Crea una cita desde el panel de administración.
    El barbero, fecha y hora vienen del slot en que hizo click el admin.
    El cliente se busca por teléfono o se crea si no existe.
    """
    # Datos del slot (pre-asignados desde el frontend)
    barber_id   = serializers.IntegerField()
    date        = serializers.DateField()
    time        = serializers.TimeField()

    # Datos del cliente
    client_name  = serializers.CharField(max_length=150)
    client_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Servicios seleccionados (al menos 1)
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )

    # Opcional
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_barber_id(self, value):
        try:
            barber = Barber.objects.get(id=value, status__name='Activo')
        except Barber.DoesNotExist:
            raise serializers.ValidationError('Barbero no encontrado o no está activo.')
        return value

    def validate_service_ids(self, value):
        services = Service.objects.filter(id__in=value, is_active=True)
        if services.count() != len(value):
            raise serializers.ValidationError('Uno o más servicios no son válidos.')
        return value

    def validate(self, attrs):
        """Verificar que el slot no esté ya ocupado."""
        from apps.appointments.availability import is_slot_available

        services       = Service.objects.filter(id__in=attrs['service_ids'])
        total_duration = sum(s.duration for s in services)

        available = is_slot_available(
            attrs['date'],
            attrs['time'],
            total_duration,
            attrs['barber_id']
        )

        if not available:
            raise serializers.ValidationError(
                'Este horario ya está ocupado para el barbero seleccionado.'
            )

        return attrs

    def create(self, validated_data):
        """
        1. Buscar o crear cliente por teléfono
        2. Generar código de confirmación
        3. Crear la cita con status 'Confirmada'
        4. Crear AppointmentService con snapshots de precio/duración
        5. Calcular y guardar totales
        """
        barber   = Barber.objects.get(id=validated_data['barber_id'])
        services = Service.objects.filter(id__in=validated_data['service_ids'])
        status   = StatusAppointment.objects.get(name='Confirmada')

        # Buscar o crear cliente por teléfono
        phone = validated_data.get('client_phone', '').strip()
        if phone:
            client, _ = Client.objects.get_or_create(
                phone=phone,
                defaults={'full_name': validated_data['client_name']}
            )
        else:
            # Sin teléfono, siempre creamos un nuevo cliente
            client = Client.objects.create(
                full_name=validated_data['client_name'],
                phone=''
            )

        # Código de confirmación único de 8 caracteres
        confirmation_code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )

        # Crear la cita
        appointment = Appointment.objects.create(
            client            = client,
            barber            = barber,
            status            = status,
            date              = validated_data['date'],
            time              = validated_data['time'],
            notes             = validated_data.get('notes', ''),
            confirmation_code = confirmation_code,
            total_amount      = 0,
            total_duration    = 0,
        )

        # Crear AppointmentService con snapshots
        total_amount   = 0
        total_duration = 0

        for service in services:
            AppointmentService.objects.create(
                appointment       = appointment,
                service           = service,
                price_snapshot    = service.price,
                duration_snapshot = service.duration,
            )
            total_amount   += service.price
            total_duration += service.duration

        # Actualizar totales
        appointment.total_amount   = total_amount
        appointment.total_duration = total_duration
        appointment.save()

        return appointment