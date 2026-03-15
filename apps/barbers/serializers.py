from rest_framework import serializers 
from django.core.validators import RegexValidator
from .models import (
    Barber, Specialty, BarberStatus, BarberSpecialty
)


color_validator = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message='El color debe tener formato hexadecimal válido. Ejemplo: #FF5733'
)

# ============================================
# SERIALIZERS PÚBLICOS
# ============================================

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id','name','description']

class BarberPublicSerializer(serializers.ModelSerializer):
    """
    Serializer público de barberos.
    Solo expone campos que el frontend necesita mostrar
    en la sección 'Nuestro Equipo'.
    """

    specialties = SpecialtySerializer(many=True, read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    avatar_url =  serializers.SerializerMethodField()

    class Meta:
        model = Barber
        fields = [
            'id',
            'name',
            'nickname',
            'description',
            'avatar_url',
            'color_code',
            'status_name',
            'specialties',
        ] 

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None
    
# ============================================
# SERIALIZERS ADMIN 
# ============================================


class SpecialtyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class BarberStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarberStatus
        fields = ['id','name','color_code','description']


class BarberAdminSerializer(serializers.ModelSerializer):

    """
    Serializer completo para el panel admin.
    Permite crear y editar barberos con todos sus campos.
    Las especialidades se manejan por separado con specialty_ids.
    """

    specialties = SpecialtySerializer(many=True, read_only=True)
    specialty_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    status_detail = BarberStatusSerializer(source='status', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    color_code = serializers.CharField(validators=[color_validator])

    class Meta:
        model = Barber
        fields = [
            'id',
            'name',
            'nickname',
            'email',
            'phone',
            'description',
            'avatar_url',
            'color_code',
            'status',
            'status_detail',
            'specialties',
            'specialty_ids',
            'created_at',
            'updated_at',
        ]
        read_only_fields=['id','created_at','updated_at']
    
    def get_avatar_url(self,obj):
        if obj.avatar:
            return obj.avatar.url
        return None
    
    def validate_specialty_ids(self,value):
        """Verifica que todas las especialidades existan."""
        if value:
            specialties = Specialty.objects.filter(id__in=value)
            if specialties.count() != len(value):
                raise serializers.ValidationError(
                    'Una o mas especialidades no son validas'
                )
        return value
    
    def create(self,validated_data):
        specialty_ids = validated_data.pop('specialty_ids', [])
        barber = Barber.objects.create(**validated_data)

        if specialty_ids:
            for specialty_id in specialty_ids:
                BarberSpecialty.objects.create(
                    barber=barber,
                    specialty_id=specialty_id
                )
        return barber
    
    def update(self, instance, validated_data):
        specialty_ids = validated_data.pop('specialty_ids',None)

        # Actualizar campos del barbero
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        #Actualizar especialidades solo si se enviaron
        if specialty_ids is not None:
            BarberSpecialty.objects.filter(barber=instance).delete()
            for specialty_id in specialty_ids:
                BarberSpecialty.objects.create(
                    barber=instance,
                    specialty_id=specialty_id
                )

        return instance
    
    




        
        


