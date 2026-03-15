# tests/test_public.py
import pytest
from datetime import date, timedelta


@pytest.mark.django_db
class TestPublicTeam:

    def test_listar_barberos_activos(self, api_client, barber, barber_status_inactivo, db):
        from apps.barbers.models import Barber
        Barber.objects.create(
            name='Inactivo',
            phone='555-9999',
            color_code='#000000',
            status=barber_status_inactivo
        )
        res = api_client.get('/api/public/team/')
        assert res.status_code == 200
        names = [b['name'] for b in res.data['results']]
        assert 'Marcus Titan' in names
        assert 'Inactivo' not in names

    def test_detalle_barbero(self, api_client, barber):
        res = api_client.get(f'/api/public/team/{barber.id}/')
        assert res.status_code == 200
        assert res.data['name'] == 'Marcus Titan'

    def test_detalle_barbero_inexistente(self, api_client):
        res = api_client.get('/api/public/team/99999/')
        assert res.status_code == 404


@pytest.mark.django_db
class TestPublicServices:

    def test_listar_servicios_activos(self, api_client, service):
        res = api_client.get('/api/public/services/')
        assert res.status_code == 200
        assert len(res.data['results']) >= 1

    def test_servicios_inactivos_no_aparecen(self, api_client, service):
        service.is_active = False
        service.save()
        res = api_client.get('/api/public/services/')
        ids = [s['id'] for s in res.data['results']]
        assert service.id not in ids


@pytest.mark.django_db
class TestPublicGallery:

    def test_listar_galeria(self, api_client, gallery_category, barber):
        from apps.gallery.models import Gallery
        Gallery.objects.create(
            category=gallery_category,
            barber=barber,
            display_order=1,
            is_active=True,
            image_url='https://res.cloudinary.com/test/image/upload/test.jpg'
        )
        res = api_client.get('/api/public/gallery/')
        assert res.status_code == 200

    def test_filtrar_galeria_por_categoria(self, api_client, gallery_category):
        res = api_client.get(f'/api/public/gallery/?category={gallery_category.slug}')
        assert res.status_code == 200

    def test_listar_categorias(self, api_client, gallery_category):
        res = api_client.get('/api/public/gallery/categories/')
        assert res.status_code == 200


@pytest.mark.django_db
class TestPublicAppointments:

    def test_disponibilidad_requiere_date_y_service_ids(self, api_client):
        res = api_client.get('/api/public/appointments/availability/')
        assert res.status_code == 400

    def test_disponibilidad_dia_no_laborable(
        self, api_client, service, business_hours, business_settings
    ):
        # Buscamos un domingo
        today = date.today()
        days_ahead = (6 - today.weekday()) % 7  # días hasta domingo
        if days_ahead == 0:
            days_ahead = 7
        sunday = today + timedelta(days=days_ahead)
        res = api_client.get(
            f'/api/public/appointments/availability/'
            f'?date={sunday}&service_ids={service.id}'
        )
        assert res.status_code == 200
        assert res.data['available_times'] == []

    def test_booking_cliente_nuevo(
        self, api_client, barber, service,
        status_confirmada, business_hours, business_settings
    ):
        tomorrow = date.today() + timedelta(days=1)
        data = {
            'client': {
                'full_name': 'Nuevo Cliente',
                'phone': '555-9999'
            },
            'date': str(tomorrow),
            'time': '10:00',
            'service_ids': [service.id],
            'barber_id': barber.id
        }
        res = api_client.post('/api/public/appointments/book/', data, format='json')
        assert res.status_code == 201
        assert 'confirmation_code' in res.data

    def test_booking_cliente_existente_reutiliza(
        self, api_client, barber, service, client_obj,
        status_confirmada, business_hours, business_settings
    ):
        tomorrow = date.today() + timedelta(days=1)
        data = {
            'client': {
                'full_name': 'Nombre Diferente',
                'phone': client_obj.phone  # mismo teléfono
            },
            'date': str(tomorrow),
            'time': '11:00',
            'service_ids': [service.id],
            'barber_id': barber.id
        }
        res = api_client.post('/api/public/appointments/book/', data, format='json')
        assert res.status_code == 201
        from apps.clients.models import Client
        # No debe crear un cliente nuevo
        assert Client.objects.filter(phone=client_obj.phone).count() == 1

    def test_booking_slot_ocupado(
        self, api_client, barber, service, appointment,
        status_confirmada, business_hours, business_settings
    ):
        data = {
            'client': {'full_name': 'Otro', 'phone': '555-8888'},
            'date': str(appointment.date),
            'time': appointment.time.strftime('%H:%M'),
            'service_ids': [service.id],
            'barber_id': barber.id
        }
        res = api_client.post('/api/public/appointments/book/', data, format='json')
        assert res.status_code == 400

    def test_consultar_status_cita(self, api_client, appointment):
        res = api_client.get(
            f'/api/public/appointments/status/?code={appointment.confirmation_code}'
        )
        assert res.status_code == 200
        assert res.data['confirmation_code'] == appointment.confirmation_code

    def test_consultar_status_codigo_invalido(self, api_client):
        res = api_client.get('/api/public/appointments/status/?code=INVALIDO')
        assert res.status_code == 404