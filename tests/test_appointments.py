# tests/test_appointments.py
import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from apps.appointments.models import Appointment, AppointmentService


@pytest.mark.django_db
class TestAgendaSchedule:

    def test_schedule_hoy(self, auth_client, business_hours, business_settings, barber):
        res = auth_client.get('/api/admin/agenda/schedule/')
        assert res.status_code == 200
        assert 'slots' in res.data
        assert 'barbers' in res.data

    def test_schedule_fecha_invalida(self, auth_client):
        res = auth_client.get('/api/admin/agenda/schedule/?date=invalida')
        assert res.status_code == 400

    def test_schedule_dia_no_laborable(
        self, auth_client, business_hours, business_settings
    ):
        today = date.today()
        days_ahead = (6 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        sunday = today + timedelta(days=days_ahead)
        res = auth_client.get(f'/api/admin/agenda/schedule/?date={sunday}')
        assert res.status_code == 200
        assert res.data['is_working_day'] is False
        assert res.data['slots'] == []


@pytest.mark.django_db
class TestChangeStatus:

    def test_cambiar_status_exitoso(
        self, auth_client, appointment, status_completada
    ):
        res = auth_client.patch(
            f'/api/admin/agenda/appointments/{appointment.id}/change-status/',
            {'status_id': status_completada.id},
            format='json'
        )
        assert res.status_code == 200
        assert res.data['new_status'] == 'Completada'

    def test_cambiar_status_id_invalido(self, auth_client, appointment):
        res = auth_client.patch(
            f'/api/admin/agenda/appointments/{appointment.id}/change-status/',
            {'status_id': 99999},
            format='json'
        )
        assert res.status_code == 400

    def test_cita_inexistente_retorna_404(self, auth_client, status_confirmada):
        res = auth_client.patch(
            '/api/admin/agenda/appointments/99999/change-status/',
            {'status_id': status_confirmada.id},
            format='json'
        )
        assert res.status_code == 404


@pytest.mark.django_db
class TestQuickAppointment:

    def test_cita_rapida_exitosa(
        self, auth_client, barber, service,
        status_confirmada, business_hours, business_settings
    ):
        tomorrow = date.today() + timedelta(days=1)
        data = {
            'barber_id': barber.id,
            'date': str(tomorrow),
            'time': '09:00',
            'client_name': 'Cliente Rapido',
            'client_phone': '555-4321',
            'service_ids': [service.id]
        }
        res = auth_client.post(
            '/api/admin/agenda/quick-appointment/', data, format='json'
        )
        assert res.status_code == 201

    def test_cita_rapida_slot_ocupado(
        self, auth_client, barber, service, appointment,
        status_confirmada, business_hours, business_settings
    ):
        data = {
            'barber_id': barber.id,
            'date': str(appointment.date),
            'time': appointment.time.strftime('%H:%M'),
            'client_name': 'Otro Cliente',
            'service_ids': [service.id]
        }
        res = auth_client.post(
            '/api/admin/agenda/quick-appointment/', data, format='json'
        )
        assert res.status_code == 400