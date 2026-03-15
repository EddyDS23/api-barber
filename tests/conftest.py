# tests/conftest.py
import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.barbers.models import Barber, BarberStatus, Specialty, BarberSpecialty
from apps.services.models import Service, ServiceType, ServiceBarber
from apps.clients.models import Client
from apps.appointments.models import Appointment, AppointmentService, StatusAppointment
from apps.gallery.models import Gallery, GalleryCategory
from apps.finance.models import FinancialTransaction, TypeTransaction, CategoryTransaction
from apps.core.models import BusinessSettings, BusinessHours, Holiday, NotificationSettings


# ─────────────────────────────────────────────
#  CLIENTE HTTP
# ─────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username='admin',
        password='admin',
        email='admin@test.com',
        is_staff=True
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username='user',
        password='testpass123',
        is_staff=False
    )


@pytest.fixture
def auth_client(api_client, admin_user, db):
    """Cliente autenticado como admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client


# ─────────────────────────────────────────────
#  CATÁLOGOS
# ─────────────────────────────────────────────

@pytest.fixture
def barber_status_activo(db):
    status, _ = BarberStatus.objects.get_or_create(
        name='Activo',
        defaults={'color_code': '#00FF00'}
    )
    return status


@pytest.fixture
def barber_status_inactivo(db):
    status, _ = BarberStatus.objects.get_or_create(
        name='Inactivo',
        defaults={'color_code': '#FF0000'}
    )
    return status


@pytest.fixture
def specialty(db):
    return Specialty.objects.create(name='Fades', description='Experto en fades')


@pytest.fixture
def service_type(db):
    return ServiceType.objects.create(
        name='Corte',
        description='Servicios de corte',
        display_order=1
    )


@pytest.fixture
def status_confirmada(db):
    status, _ = StatusAppointment.objects.get_or_create(name='Confirmada')
    return status


@pytest.fixture
def status_cancelada(db):
    status, _ = StatusAppointment.objects.get_or_create(name='Cancelada')
    return status


@pytest.fixture
def status_completada(db):
    status, _ = StatusAppointment.objects.get_or_create(name='Completada')
    return status


@pytest.fixture
def type_ingreso(db):
    t, _ = TypeTransaction.objects.get_or_create(name='Ingreso')
    return t


@pytest.fixture
def type_egreso(db):
    t, _ = TypeTransaction.objects.get_or_create(name='Egreso')
    return t


@pytest.fixture
def category_servicio(db):
    c, _ = CategoryTransaction.objects.get_or_create(name='Servicio')
    return c


# ─────────────────────────────────────────────
#  ENTIDADES PRINCIPALES
# ─────────────────────────────────────────────

@pytest.fixture
def barber(db, barber_status_activo):
    return Barber.objects.create(
        name='Marcus Titan',
        nickname='El Artista',
        phone='555-0001',
        color_code='#FF5733',
        status=barber_status_activo
    )


@pytest.fixture
def barber2(db, barber_status_activo):
    return Barber.objects.create(
        name='Carlos Gómez',
        phone='555-0002',
        color_code='#3498DB',
        status=barber_status_activo
    )


@pytest.fixture
def service(db, service_type, barber):
    svc = Service.objects.create(
        name='Corte Clásico',
        description='Corte tradicional',
        short_description='Corte clásico',
        price=Decimal('15.00'),
        duration=30,
        service_type=service_type,
        is_active=True
    )
    ServiceBarber.objects.create(service=svc, barber=barber)
    return svc


@pytest.fixture
def service2(db, service_type, barber):
    svc = Service.objects.create(
        name='Barba Completa',
        description='Arreglo de barba',
        short_description='Barba',
        price=Decimal('10.00'),
        duration=20,
        service_type=service_type,
        is_active=True
    )
    ServiceBarber.objects.create(service=svc, barber=barber)
    return svc


@pytest.fixture
def client_obj(db):
    return Client.objects.create(
        full_name='Juan Pérez',
        phone='5551234',
        email='juan@test.com'
    )


@pytest.fixture
def appointment(db, barber, client_obj, service, status_confirmada):
    apt = Appointment.objects.create(
        barber=barber,
        client=client_obj,
        status=status_confirmada,
        date=date.today() + timedelta(days=1),
        time=time(10, 0),
        total_amount=Decimal('15.00'),
        total_duration=30,
        confirmation_code='TEST0001'
    )
    AppointmentService.objects.create(
        appointment=apt,
        service=service,
        price_snapshot=service.price,
        duration_snapshot=service.duration
    )
    return apt


@pytest.fixture
def gallery_category(db):
    return GalleryCategory.objects.create(
        name='Fades y Degradados',
        slug='fades',
        display_order=1
    )


@pytest.fixture
def business_hours(db):
    """Crea horarios de lunes a sábado 09:00-18:00."""
    hours = []
    for day in range(0, 7):  # 0=Dom ... 6=Sab
        is_working = day != 0  # Domingo cerrado
        h = BusinessHours.objects.create(
            day_of_week=day,
            is_working=is_working,
            opening_time=time(9, 0) if is_working else None,
            closing_time=time(18, 0) if is_working else None
        )
        hours.append(h)
    return hours


@pytest.fixture
def business_settings(db):
    obj, _ = BusinessSettings.objects.get_or_create(
        id=1,
        defaults={
            'business_name': 'Barbería Test',
            'address': 'Calle Test 123',
            'phone': '555-0000',
            'time_slot_duration': 30,
            'booking_enabled': True,
        }
    )
    return obj


@pytest.fixture
def transaction_ingreso(db, type_ingreso, category_servicio, appointment):
    return FinancialTransaction.objects.create(
        type=type_ingreso,
        category=category_servicio,
        concept='Pago corte',
        amount=Decimal('15.00'),
        date=date.today(),
        appointment=appointment
    )