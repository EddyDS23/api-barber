from django.db import models
from cloudinary.models import CloudinaryField
from apps.barbers.models import Barber

# Create your models here.
class ServiceType(models.Model):

    """
    Tabla: type_services
    Catálogo de tipos: Corte, Barba, Tratamiento, Combo, Especial
    """

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'type_services'
        verbose_name = 'Tipo de Servicio'
        verbose_name_plural = 'Tipos de Servicios'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
    

class Service(models.Model):
    """
    Tabla: services
    Servicios ofrecidos por la barbería
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    short_description = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text='Duracion en minutos')
    image_url = CloudinaryField('service_image', blank=True, null=True)
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='service_type_id',
        related_name='services'
    )
    barbers = models.ManyToManyField(
        Barber,
        through='ServiceBarber',
        related_name='services'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='services'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    
    def __str__(self):
        return f"{self.name} - ${self.price}"
    

class ServiceBarber(models.Model):
    """
    Tabla: service_barbers
    Tabla intermedia M:N entre Service y Barber
    Un servicio puede ser realizado por varios barberos
    """

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        db_column='service_id', 
    )
    barber = models.ForeignKey(
        Barber,
        on_delete=models.CASCADE,
        db_column='barber_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='service_barbers'
        unique_together = ['service', 'barber']
        verbose_name = 'Barbero del Servicio'
        verbose_name_plural = 'Barberos del Servicio'

    def __str__(self):
        return f"{self.service.name} - {self.barber.name}"
    
    

