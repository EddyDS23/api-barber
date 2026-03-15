# tests/test_reports.py
import pytest
from datetime import date, timedelta
from decimal import Decimal
from apps.finance.models import FinancialTransaction


@pytest.fixture
def transactions_mes(db, type_ingreso, category_servicio):
    """Crea varias transacciones en el mes actual."""
    transactions = []
    for i in range(5):
        t = FinancialTransaction.objects.create(
            type=type_ingreso,
            category=category_servicio,
            concept=f'Ingreso {i}',
            amount=Decimal('100.00'),
            date=date.today() - timedelta(days=i)
        )
        transactions.append(t)
    return transactions


@pytest.mark.django_db
class TestIncomeChart:

    def test_income_chart_period_week(self, auth_client, transaction_ingreso):
        res = auth_client.get('/api/admin/reports/income-chart/?period=week')
        assert res.status_code == 200
        assert 'data' in res.data
        assert len(res.data['data']) == 7

    def test_income_chart_period_today(self, auth_client, transaction_ingreso):
        res = auth_client.get('/api/admin/reports/income-chart/?period=today')
        assert res.status_code == 200
        assert 'data' in res.data
        assert len(res.data['data']) == 24  # 24 horas

    def test_income_chart_period_month(self, auth_client, transactions_mes):
        res = auth_client.get('/api/admin/reports/income-chart/?period=month')
        assert res.status_code == 200
        assert 'data' in res.data
        assert len(res.data['data']) >= 28  # días del mes

    def test_income_chart_period_year(self, auth_client, transaction_ingreso):
        res = auth_client.get('/api/admin/reports/income-chart/?period=year')
        assert res.status_code == 200
        assert 'data' in res.data
        assert len(res.data['data']) == 12  # 12 meses

    def test_income_chart_default_es_week(self, auth_client):
        res = auth_client.get('/api/admin/reports/income-chart/')
        assert res.status_code == 200
        assert 'data' in res.data

    def test_income_chart_estructura_item(self, auth_client, transaction_ingreso):
        res = auth_client.get('/api/admin/reports/income-chart/?period=week')
        assert res.status_code == 200
        item = res.data['data'][0]
        assert 'label' in item or 'day' in item or 'date' in item
        assert 'income' in item

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/reports/income-chart/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestTopServices:

    def test_top_services_estructura(
        self, auth_client, appointment, status_completada
    ):
        appointment.status = status_completada
        appointment.save()
        res = auth_client.get('/api/admin/reports/top-services/')
        assert res.status_code == 200
        assert 'services' in res.data

    def test_top_services_sin_datos(self, auth_client):
        res = auth_client.get('/api/admin/reports/top-services/')
        assert res.status_code == 200
        assert 'services' in res.data
        assert isinstance(res.data['services'], list)

    def test_top_services_campos(self, auth_client, appointment, status_completada):
        appointment.status = status_completada
        appointment.save()
        res = auth_client.get('/api/admin/reports/top-services/')
        assert res.status_code == 200
        if res.data['services']:
            service = res.data['services'][0]
            assert 'rank' in service
            assert 'name' in service
            assert 'count' in service


@pytest.mark.django_db
class TestTopBarbers:

    def test_top_barbers_estructura(
        self, auth_client, appointment, status_completada
    ):
        appointment.status = status_completada
        appointment.save()
        res = auth_client.get('/api/admin/reports/top-barbers/')
        assert res.status_code == 200
        assert 'barbers' in res.data

    def test_top_barbers_sin_datos(self, auth_client):
        res = auth_client.get('/api/admin/reports/top-barbers/')
        assert res.status_code == 200
        assert isinstance(res.data['barbers'], list)

    def test_top_barbers_campos(self, auth_client, appointment, status_completada):
        appointment.status = status_completada
        appointment.save()
        res = auth_client.get('/api/admin/reports/top-barbers/')
        assert res.status_code == 200
        if res.data['barbers']:
            barber = res.data['barbers'][0]
            assert 'rank' in barber
            assert 'name' in barber
            assert 'appointments_count' in barber

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/reports/top-barbers/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestOccupancyHeatmap:

    def test_heatmap_estructura(self, auth_client, appointment):
        res = auth_client.get('/api/admin/reports/occupancy-heatmap/')
        assert res.status_code == 200
        assert 'days' in res.data
        assert 'hours' in res.data
        assert 'data' in res.data
        assert 'peak_threshold' in res.data

    def test_heatmap_dias_son_lista(self, auth_client):
        res = auth_client.get('/api/admin/reports/occupancy-heatmap/')
        assert res.status_code == 200
        assert isinstance(res.data['days'], list)
        assert isinstance(res.data['hours'], list)

    def test_heatmap_items_tienen_campos(self, auth_client, appointment):
        res = auth_client.get('/api/admin/reports/occupancy-heatmap/')
        assert res.status_code == 200
        if res.data['data']:
            item = res.data['data'][0]
            assert 'day' in item
            assert 'hour' in item
            assert 'count' in item
            assert 'is_peak' in item

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/reports/occupancy-heatmap/')
        assert res.status_code == 401