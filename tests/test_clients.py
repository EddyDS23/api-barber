# tests/test_clients.py
import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from apps.clients.models import Client
from apps.appointments.models import Appointment, AppointmentService


@pytest.mark.django_db
class TestClientsCRUD:

    def test_listar_clientes(self, auth_client, client_obj):
        res = auth_client.get('/api/admin/clients/')
        assert res.status_code == 200
        assert res.data['count'] >= 1

    def test_detalle_cliente(self, auth_client, client_obj):
        res = auth_client.get(f'/api/admin/clients/{client_obj.id}/')
        assert res.status_code == 200
        assert res.data['full_name'] == 'Juan Pérez'
        assert res.data['phone'] == '5551234'

    def test_crear_cliente(self, auth_client):
        data = {
            'full_name': 'Nuevo Cliente',
            'phone': '5558888',
            'email': 'nuevo@test.com'
        }
        res = auth_client.post('/api/admin/clients/', data)
        assert res.status_code == 201
        assert res.data['full_name'] == 'Nuevo Cliente'

    def test_crear_cliente_telefono_duplicado(self, auth_client, client_obj):
        data = {
            'full_name': 'Otro Cliente',
            'phone': client_obj.phone  # ya existe
        }
        res = auth_client.post('/api/admin/clients/', data)
        assert res.status_code == 400

    def test_crear_cliente_email_duplicado(self, auth_client, client_obj):
        data = {
            'full_name': 'Otro Cliente',
            'phone': '5557777',
            'email': client_obj.email  # ya existe
        }
        res = auth_client.post('/api/admin/clients/', data)
        assert res.status_code == 400

    def test_actualizar_cliente(self, auth_client, client_obj):
        res = auth_client.patch(
            f'/api/admin/clients/{client_obj.id}/',
            {'full_name': 'Juan Actualizado'},
            format='json'
        )
        assert res.status_code == 200
        assert res.data['full_name'] == 'Juan Actualizado'

    def test_eliminar_cliente_sin_citas_activas(self, auth_client, client_obj):
        res = auth_client.delete(f'/api/admin/clients/{client_obj.id}/')
        assert res.status_code == 204

    def test_eliminar_cliente_con_citas_activas_falla(
        self, auth_client, client_obj, appointment
    ):
        # appointment ya tiene status 'Confirmada' (activa)
        res = auth_client.delete(f'/api/admin/clients/{client_obj.id}/')
        assert res.status_code == 400
        assert 'citas activas' in res.data['error'].lower()

    def test_cliente_inexistente_retorna_404(self, auth_client):
        res = auth_client.get('/api/admin/clients/99999/')
        assert res.status_code == 404

    def test_buscar_cliente_por_nombre(self, auth_client, client_obj):
        res = auth_client.get('/api/admin/clients/?search=Juan')
        assert res.status_code == 200
        assert res.data['count'] >= 1

    def test_buscar_cliente_por_telefono(self, auth_client, client_obj):
        res = auth_client.get(f'/api/admin/clients/?search={client_obj.phone}')
        assert res.status_code == 200
        assert res.data['count'] >= 1

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/clients/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestClientHistory:

    def test_historial_citas_cliente(self, auth_client, client_obj, appointment):
        res = auth_client.get(
            f'/api/admin/clients/{client_obj.id}/appointments/'
        )
        assert res.status_code == 200
        assert isinstance(res.data, list)
        assert len(res.data) >= 1

    def test_historial_incluye_campos_correctos(
        self, auth_client, client_obj, appointment
    ):
        res = auth_client.get(
            f'/api/admin/clients/{client_obj.id}/appointments/'
        )
        assert res.status_code == 200
        apt = res.data[0]
        assert 'date' in apt
        assert 'time' in apt
        assert 'barber' in apt
        assert 'status' in apt
        assert 'services' in apt
        assert 'total_amount' in apt
        assert 'confirmation_code' in apt

    def test_historial_cliente_sin_citas(self, auth_client):
        cliente_nuevo = Client.objects.create(
            full_name='Sin Citas',
            phone='5550000'
        )
        res = auth_client.get(
            f'/api/admin/clients/{cliente_nuevo.id}/appointments/'
        )
        assert res.status_code == 200
        assert res.data == []

    def test_campo_total_spent(self, auth_client, client_obj, appointment, status_completada):
        appointment.status = status_completada
        appointment.save()
        res = auth_client.get(f'/api/admin/clients/{client_obj.id}/')
        assert res.status_code == 200
        assert 'total_spent' in res.data
        assert float(res.data['total_spent']) >= 0

    def test_campo_last_visit(self, auth_client, client_obj, appointment, status_completada):
        appointment.status = status_completada
        appointment.save()
        res = auth_client.get(f'/api/admin/clients/{client_obj.id}/')
        assert res.status_code == 200
        assert 'last_visit' in res.data