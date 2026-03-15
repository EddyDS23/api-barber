# tests/test_finance.py
import pytest
from decimal import Decimal
from datetime import date


@pytest.mark.django_db
class TestFinanceSummary:

    def test_summary_retorna_estructura(
        self, auth_client, type_ingreso, type_egreso,
        category_servicio, transaction_ingreso
    ):
        res = auth_client.get('/api/admin/finance/summary/')
        assert res.status_code == 200
        assert 'income' in res.data
        assert 'expenses' in res.data
        assert 'net_profit' in res.data
        assert 'current' in res.data['income']
        assert 'percent_change' in res.data['income']

    def test_summary_sin_jwt(self, api_client):
        res = api_client.get('/api/admin/finance/summary/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestTransactions:

    def test_listar_transacciones(self, auth_client, transaction_ingreso):
        res = auth_client.get('/api/admin/finance/transactions/')
        assert res.status_code == 200
        assert len(res.data['results']) >= 1

    def test_crear_transaccion(
        self, auth_client, type_ingreso, category_servicio
    ):
        data = {
            'type': type_ingreso.id,
            'category': category_servicio.id,
            'concept': 'Pago test',
            'amount': '50.00',
            'date': str(date.today())
        }
        res = auth_client.post(
            '/api/admin/finance/transactions/', data, format='json'
        )
        assert res.status_code == 201

    def test_crear_transaccion_amount_cero_falla(
        self, auth_client, type_ingreso, category_servicio
    ):
        data = {
            'type': type_ingreso.id,
            'category': category_servicio.id,
            'concept': 'Monto cero',
            'amount': '0.00',
            'date': str(date.today())
        }
        res = auth_client.post(
            '/api/admin/finance/transactions/', data, format='json'
        )
        assert res.status_code == 400

    def test_filtrar_por_tipo(self, auth_client, transaction_ingreso, type_ingreso):
        res = auth_client.get(
            f'/api/admin/finance/transactions/?type={type_ingreso.id}'
        )
        assert res.status_code == 200

    def test_filtrar_por_rango_fechas(self, auth_client, transaction_ingreso):
        today = str(date.today())
        res = auth_client.get(
            f'/api/admin/finance/transactions/?date_from={today}&date_to={today}'
        )
        assert res.status_code == 200
        assert len(res.data['results']) >= 1

    def test_eliminar_tipo_con_transacciones_falla(
        self, auth_client, type_ingreso, transaction_ingreso
    ):
        res = auth_client.delete(f'/api/admin/finance/types/{type_ingreso.id}/')
        assert res.status_code == 400