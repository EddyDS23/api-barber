from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.

class BarberStatus(models.Model):

    """
    Tabla: barber_status
    Catálogo de estados: Activo, Vacaciones, Inactivo
    Ya tiene datos insertados desde el schema SQL
    """

    name = models.CharField(max_length=20, unique=True)
    color_code = models.CharField(max_length=7)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'barber_status'
        verbose_name = 'Estado de Barbero'
        verbose_name_plural = 'Estados de Barberos'

    def __str__(self):
        return self.name


class Specialty(models.Model):

    """
    Tabla: specialties
    Catálogo de especialidades de barberos
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'specialties'   
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
    
    def __str__(self):
        return self.name
    

class Barber(models.Model):
    """
    Tabla: barbers
    Barberos del negocio con su info completa
    """

    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    # CloudinaryField almacena la URL de la imagen en Cloudinary
    # blank=True, null=True porque el avatar es opcional al crears
    avatar = CloudinaryField('barber_avatar', blank=True, null=True)

    color_code = models.CharField(max_length=7)

    status = models.ForeignKey(
        BarberStatus,
        on_delete=models.RESTRICT,
        db_column='status_id',
        default=1
    )

    specialties = models.ManyToManyField(
        Specialty,
        through='BarberSpecialty',
        related_name='barbers'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='barbers'
        verbose_name='Barbero'
        verbose_name_plural='Barberos'
        ordering = ['name']

    
    def __str__(self):
        return f"{self.name} ({self.nickname})" if self.nickname else self.name
    

class BarberSpecialty(models.Model):
    """
    Tabla: barber_specialties
    Tabla intermedia M:N entre Barber y Specialty
    """

    barber = models.ForeignKey(
        Barber,
        on_delete=models.CASCADE,
        db_column='barber_id'
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        db_column='specialty_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'barber_specialties'
        unique_together = ['barber', 'specialty']
        verbose_name = 'Especialidad del Barbero'
        verbose_name_plural = 'Especialidades de Barberos'

    def __str__(self):
        return f"{self.barber.name} -> {self.specialty.name}"

    