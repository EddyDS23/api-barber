from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.
class BusinessSettings(models.Model):
    """
    Tabla: business_settings
    Configuración general del negocio.

    Es un Singleton → solo existe 1 registro con id=1.
    El método save() fuerza que el id siempre sea 1,
    así nunca se crea un segundo registro accidentalmente.
    """

    id = models.IntegerField(primary_key=True, default=1)

     # Información general
    business_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    logo_url = CloudinaryField('business_logo', blank=True, null=True)

    # Redes sociales
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    tiktok_url = models.URLField(blank=True, null=True)

    # Campos deprecated (usar business_hours en su lugar)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    time_slot_duration = models.IntegerField(default=30)

    # Reglas de reservas
    booking_enabled = models.BooleanField(default=True)
    max_days_advance = models.IntegerField(default=30)
    min_hours_before = models.IntegerField(default=2)
    allow_cancellations = models.BooleanField(default=True)
    cancellation_hours_before = models.IntegerField(default=24)
    require_deposit = models.BooleanField(default=False)
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_settings'
        verbose_name = 'Configuración del Negocio'
        verbose_name_plural = 'Configuración del Negocio'

    def save(self, *args, **kwargs):
        # Fuerza que siempre sea id=1 (Singleton)
        self.id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.business_name

class BusinessHours(models.Model):
    """
    Tabla: business_hours
    Horarios de operación por día de la semana.
    7 registros fijos (uno por día).

    day_of_week:
        0 = Domingo
        1 = Lunes
        2 = Martes
        3 = Miércoles
        4 = Jueves
        5 = Viernes
        6 = Sábado
    """
    DAYS = [
        (0, 'Domingo'),
        (1, 'Lunes'),
        (2, 'Martes'),
        (3, 'Miércoles'),
        (4, 'Jueves'),
        (5, 'Viernes'),
        (6, 'Sábado'),
    ]

    day_of_week = models.IntegerField(choices=DAYS, unique=True)
    is_working = models.BooleanField(default=True)
    # null=True porque el domingo puede estar cerrado y no tener horario
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_hours'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios del Negocio'
        ordering = ['day_of_week']

    def __str__(self):
        estado = 'Abierto' if self.is_working else 'Cerrado'
        return f"{self.get_day_of_week_display()} - {estado}"


class Holiday(models.Model):
    """
    Tabla: holidays
    Días feriados o excepciones donde el negocio no trabaja.
    El sistema de disponibilidad consulta esta tabla antes
    de mostrar slots disponibles.
    """
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'holidays'
        verbose_name = 'Día Feriado'
        verbose_name_plural = 'Días Feriados'
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.reason}"
    

class NotificationSettings(models.Model):
    """
    Tabla: notification_settings
    Configuración de notificaciones automáticas.
    También es un Singleton → solo existe 1 registro con id=1.
    """
    id = models.IntegerField(primary_key=True, default=1)
    sms_reminder_enabled = models.BooleanField(default=False)
    sms_hours_before = models.IntegerField(default=24)
    email_promotions_enabled = models.BooleanField(default=False)
    whatsapp_enabled = models.BooleanField(default=False)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_connected = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_settings'
        verbose_name = 'Configuración de Notificaciones'
        verbose_name_plural = 'Configuración de Notificaciones'

    def save(self, *args, **kwargs):
        self.id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuración de Notificaciones"