# tests/test_dashboard.py
import pytest


@pytest.mark.django_db
class TestDashboardStats:

    def test_stats_estructura(self, auth_client, transaction_ingreso, appointment):
        res = auth_client.get('/api/admin/dashboard/stats/')
        assert res.status_code == 200
        assert 'total_income_month' in res.data
        assert 'appointments_today' in res.data
        assert 'cancellations_month' in res.data
        assert 'top_barber' in res.data

    def test_weekly_performance(self, auth_client):
        res = auth_client.get('/api/admin/dashboard/weekly-performance/')
        assert res.status_code == 200
        assert 'days' in res.data
        assert len(res.data['days']) == 7

    def test_upcoming_appointments(self, auth_client, appointment):
        res = auth_client.get('/api/admin/dashboard/upcoming-appointments/')
        assert res.status_code == 200
        assert isinstance(res.data, list)

    def test_upcoming_limit(self, auth_client):
        res = auth_client.get('/api/admin/dashboard/upcoming-appointments/?limit=2')
        assert res.status_code == 200
        assert len(res.data) <= 2

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/dashboard/stats/')
        assert res.status_code == 401