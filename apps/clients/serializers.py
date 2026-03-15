from rest_framework import serializers
from .models import Client

class ClientAdminSerializer(serializers.ModelSerializer):
    """
    Serializer completo para gestión de clientes.
    Incluye campos calculados: última visita y total gastado.
    """

    last_visit = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id',
            'full_name',
            'phone',
            'email',
            'notes',
            'last_visit',
            'total_spent',
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_visit(self, obj):
        """
        Fecha de la última cita COMPLETADA del cliente.
        """
        last_appointment = obj.appointments.filter(
            status__name='Completada'
        ).order_by('-date').first()

        if last_appointment:
            return str(last_appointment.date)
        return None

    def get_total_spent(self, obj):
        """
        Suma total de todas las citas COMPLETADAS del cliente.
        """
        from django.db.models import Sum
        total = obj.appointments.filter(
            status__name='Completada'
        ).aggregate(
            total=Sum('total_amount')
        )['total']

        return str(total) if total else '0.00'
    

class ClientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear clientes.
    Más simple, sin campos calculados.
    """
    class Meta:
        model = Client
        fields = [
            'id',
            'full_name',
            'phone',
            'email',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_phone(self, value):
        """Verifica que el teléfono no esté duplicado."""
        instance = self.instance  # None si es creación, objeto si es edición
        if Client.objects.filter(phone=value).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                'Ya existe un cliente con este teléfono.'
            )
        return value

    def validate_email(self, value):
        """Verifica que el email no esté duplicado."""
        if not value:
            return value
        instance = self.instance
        if Client.objects.filter(email=value).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                'Ya existe un cliente con este email.'
            )
        return value
