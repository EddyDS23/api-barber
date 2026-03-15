# tests/test_settings.py
import pytest
from datetime import date


@pytest.mark.django_db
class TestBusinessSettings:

    def test_get_business_info(self, auth_client, business_settings):
        res = auth_client.get('/api/admin/settings/business-info/')
        assert res.status_code == 200
        assert 'business_name' in res.data

    def test_patch_business_info(self, auth_client, business_settings):
        res = auth_client.patch(
            '/api/admin/settings/business-info/',
            {'business_name': 'Nueva Barbería'},
            format='json'
        )
        assert res.status_code == 200
        assert res.data['business_name'] == 'Nueva Barbería'

    def test_get_business_hours(self, auth_client, business_hours):
        res = auth_client.get('/api/admin/settings/business-hours/')
        assert res.status_code == 200
        assert len(res.data) == 7

    def test_get_holidays(self, auth_client):
        res = auth_client.get('/api/admin/settings/holidays/')
        assert res.status_code == 200

    def test_crear_feriado(self, auth_client):
        res = auth_client.post('/api/admin/settings/holidays/', {
            'date': str(date.today() + __import__('datetime').timedelta(days=30)),
            'reason': 'Día de prueba'
        })
        assert res.status_code == 201

    def test_eliminar_feriado(self, auth_client):
        from apps.core.models import Holiday
        holiday = Holiday.objects.create(
            date=date.today() + __import__('datetime').timedelta(days=60),
            reason='Test'
        )
        res = auth_client.delete(f'/api/admin/settings/holidays/{holiday.id}/')
        assert res.status_code == 200

    def test_get_notifications(self, auth_client):
        res = auth_client.get('/api/admin/settings/notifications/')
        assert res.status_code == 200

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/settings/business-info/')
        assert res.status_code == 401