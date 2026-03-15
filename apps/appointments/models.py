from django.db import models

from apps.barbers.models import Barber
from apps.services.models import Service
from apps.clients.models import Client

# Create your models here.
class StatusAppointment(models.Model):

    """
    Tabla: status_appointments
    Catálogo de estados de citas:
    Pendiente, Confirmada, En progreso, Completada, Cancelada, No asistió
    """

    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'status_appointments'
        verbose_name = 'Estado de Cita'
        verbose_name_plural = 'Estados de Citas'
    
    def __str__(self):
        return self.name
    

class Appointment(models.Model):

    """
    Tabla: appointments
    Citas agendadas. Es el núcleo del sistema.
    
    Puntos clave:
    - unique_together en (barber, date, time) → un barbero no puede
      tener dos citas al mismo tiempo
    - confirmation_code → código único que el cliente puede usar
      para consultar su cita públicamente
    - total_amount y total_duration se calculan al crear la cita
      sumando los servicios seleccionados
    """
     
    barber = models.ForeignKey(
        Barber,
        on_delete=models.RESTRICT,
        db_column='barber_id',
        related_name='appointments'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.RESTRICT,
        db_column='client_id',
        related_name='appointments'
    )
    status = models.ForeignKey(
        StatusAppointment,
        on_delete=models.RESTRICT,
        db_column='status_id'
    )
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_duration = models.IntegerField(
        default=0,
        help_text='Duracion total en minutos'
    )
    confirmation_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )
    services = models.ManyToManyField(
        Service,
        through='AppointmentService',
        related_name='appointments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        verbose_name = 'Cita'
        verbose_name_plural='Citas'
        unique_together = ['barber','date','time']
        ordering = ['-date','-time']

    def __str__(self):
        return f"Cita #{self.id} - {self.client.full_name} ({self.date} {self.time})"
    

class AppointmentService(models.Model):
    """
    Tabla: appointments_services
    Tabla intermedia M:N entre Appointment y Service.
    
    Tiene snapshot de precio y duración porque si el admin
    cambia el precio de un servicio en el futuro, las citas
    anteriores deben conservar el precio original al momento
    de la reserva.
    """

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        db_column='appointment_id'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.RESTRICT,
        db_column='service_id'
    )
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    duration_snapshot = models.IntegerField()

    class Meta:
        db_table='appointments_services'
        verbose_name = 'Servicio de la Cita'
        verbose_name_plural = 'Servicios de la Cita'

    
    def __str__(self):
        return f"Cita #{self.appointment.id} -> {self.service.name}"




