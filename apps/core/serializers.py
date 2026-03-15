# apps/core/serializers.py

from rest_framework import serializers
from .models import BusinessSettings, BusinessHours, Holiday, NotificationSettings


# ─────────────────────────────────────────────────────────────
#  Apartado 1: Información General
# ─────────────────────────────────────────────────────────────

class BusinessInfoSerializer(serializers.ModelSerializer):

    # CloudinaryField retorna un objeto, necesitamos la URL como string
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model  = BusinessSettings
        fields = [
            'business_name',
            'address',
            'phone',
            'email',
            'logo_url',       # solo lectura — el upload es por endpoint separado
            'facebook_url',
            'instagram_url',
            'tiktok_url',
        ]
        # logo_url no se edita desde este endpoint, solo desde upload-logo
        read_only_fields = ['logo_url']

    def get_logo_url(self, obj):
        """Retorna la URL completa de Cloudinary o null si no hay logo."""
        if obj.logo_url:
            return obj.logo_url.url
        return None

    def validate_business_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre del negocio es requerido.")
        return value.strip()

    def validate_address(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("La dirección es requerida.")
        return value.strip()

    def validate_phone(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El teléfono es requerido.")
        return value.strip()


# ─────────────────────────────────────────────────────────────
#  Apartado 2: Reglas de Reservas
# ─────────────────────────────────────────────────────────────

class BookingRulesSerializer(serializers.ModelSerializer):
    """
    GET/PATCH /api/admin/settings/booking-rules/

    Controla las reglas del sistema de agendamiento público.
    También es singleton id=1.
    """
    class Meta:
        model  = BusinessSettings
        fields = [
            'booking_enabled',
            'max_days_advance',
            'min_hours_before',
            'allow_cancellations',
            'cancellation_hours_before',
            'require_deposit',
            'deposit_amount',
            'time_slot_duration',
        ]

    def validate_max_days_advance(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Debe ser al menos 1 día.")
        return value

    def validate_min_hours_before(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("No puede ser negativo.")
        return value

    def validate_deposit_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El monto de la seña no puede ser negativo.")
        return value

    def validate_time_slot_duration(self, value):
        valid_durations = [15, 30, 45, 60]
        if value not in valid_durations:
            raise serializers.ValidationError(
                f"Duración de slot inválida. Opciones: {valid_durations}"
            )
        return value


# ─────────────────────────────────────────────────────────────
#  Apartado 3a: Horarios de la semana
# ─────────────────────────────────────────────────────────────

class BusinessHoursSerializer(serializers.ModelSerializer):
    """
    Serializer para un día del horario semanal.

    PUT /api/admin/settings/business-hours/
    Recibe un array de 7 días y actualiza todos de una vez.

    Schema DB: day_of_week → 0=Domingo, 1=Lunes ... 6=Sábado
    """
    # Nombre legible del día para el frontend (solo lectura)
    day_name = serializers.SerializerMethodField(read_only=True)

    DAY_NAMES = {
        0: 'Domingo', 1: 'Lunes', 2: 'Martes',
        3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado'
    }

    class Meta:
        model  = BusinessHours
        fields = [
            'id',
            'day_of_week',
            'day_name',
            'is_working',
            'opening_time',
            'closing_time',
        ]

    def get_day_name(self, obj):
        return self.DAY_NAMES.get(obj.day_of_week, '')

    def validate(self, attrs):
        """
        Si el día es laborable, apertura y cierre son requeridos.
        Si no es laborable, los horarios pueden ser null.
        """
        is_working   = attrs.get('is_working', False)
        opening_time = attrs.get('opening_time')
        closing_time = attrs.get('closing_time')

        if is_working:
            if not opening_time:
                raise serializers.ValidationError(
                    {'opening_time': 'La hora de apertura es requerida para días laborables.'}
                )
            if not closing_time:
                raise serializers.ValidationError(
                    {'closing_time': 'La hora de cierre es requerida para días laborables.'}
                )
            if opening_time >= closing_time:
                raise serializers.ValidationError(
                    {'closing_time': 'La hora de cierre debe ser mayor a la de apertura.'}
                )

        return attrs


# ─────────────────────────────────────────────────────────────
#  Apartado 3b: Días feriados
# ─────────────────────────────────────────────────────────────

class HolidaySerializer(serializers.ModelSerializer):
    """
    GET  /api/admin/settings/holidays/
    POST /api/admin/settings/holidays/
    DELETE /api/admin/settings/holidays/{id}/
    """
    class Meta:
        model  = Holiday
        fields = ['id', 'date', 'reason']

    def validate_date(self, value):
        if not value:
            raise serializers.ValidationError("La fecha es requerida.")
        # Verificar que no exista ya un feriado en esa fecha
        qs = Holiday.objects.filter(date=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un feriado registrado en esa fecha.")
        return value


# ─────────────────────────────────────────────────────────────
#  Apartado 4: Notificaciones
# ─────────────────────────────────────────────────────────────

class NotificationSettingsSerializer(serializers.ModelSerializer):
    """
    GET/PATCH /api/admin/settings/notifications/

    Singleton id=1 — igual que BusinessSettings.
    """
    class Meta:
        model  = NotificationSettings
        fields = [
            'sms_reminder_enabled',
            'sms_hours_before',
            'email_promotions_enabled',
            'whatsapp_enabled',
            'whatsapp_number',
            'whatsapp_connected',
        ]

    def validate_sms_hours_before(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Debe ser al menos 1 hora antes.")
        return value