from rest_framework import serializers
from .models import (ServiceType, Service)
from .models import ServiceType, ServiceBarber
from apps.barbers.models import Barber
from apps.barbers.serializers import BarberPublicSerializer



# ============================================
# SERIALIZERS PÚBLICOS 
# ============================================

class ServiceTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceType
        fields = ['id','name','description']


class ServicePublicSerializer(serializers.ModelSerializer):

    """
    Serializer público de servicios.
    Muestra la info que el cliente necesita para elegir
    qué servicio quiere agendar.
    """

    service_type = ServiceTypeSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'description',
            'short_description',
            'price',
            'duration',
            'image',
            'service_type'
        ]

    def get_image(self,obj):
        if obj.image_url:
            return obj.image_url.url
        return None



# ============================================
# SERIALIZERS ADMIN 
# ============================================

class ServiceTypeAdminSerializer(serializers.ModelSerializer):
    """
    Serializer completo para gestión de tipos de servicios.
    """
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'description', 'display_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ServiceAdminSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el panel admin.
    Permite crear y editar servicios con todos sus campos.
    Los barberos asignados se manejan con barber_ids.
    """

    service_type_detail = ServiceTypeSerializer(
        source='service_type',
        read_only = True
    ) 
    barbers = BarberPublicSerializer(many=True, read_only=True)
    barber_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'description',
            'short_description',
            'price',
            'duration',
            'image',
            'image_url',
            'service_type',
            'service_type_detail',
            'barbers',
            'barber_ids',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id','created_at','updated_at']
        extra_kwargs = {
            'image_url': {'write_only':True, 'required':False}
        }


    def get_image(self,obj):
        if obj.image_url:
            return obj.image_url.url
        return None
    

    def validate_barber_ids(self, value):
        """Verifica que todos los barberos existan y estén activos."""
        if value:
            barbers = Barber.objects.filter(id__in=value)
            if barbers.count() != len(value):
                raise serializers.ValidationError(
                    'Uno o más barberos no son válidos.'
                )
        return value

    def create(self, validated_data):
        barber_ids = validated_data.pop('barber_ids', [])
        service = Service.objects.create(**validated_data)

        # Asignar barberos
        if barber_ids:
            for barber_id in barber_ids:
                ServiceBarber.objects.create(
                    service=service,
                    barber_id=barber_id
                )
        return service

    def update(self, instance, validated_data):
        barber_ids = validated_data.pop('barber_ids', None)

        # Actualizar campos del servicio
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar barberos solo si se enviaron
        if barber_ids is not None:
            ServiceBarber.objects.filter(service=instance).delete()
            for barber_id in barber_ids:
                ServiceBarber.objects.create(
                    service=instance,
                    barber_id=barber_id
                )

        return instance



