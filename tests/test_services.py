# tests/test_services.py
import pytest
from decimal import Decimal


@pytest.mark.django_db
class TestServicesCRUD:

    def test_listar_servicios_admin(self, auth_client, service):
        res = auth_client.get('/api/admin/services/')
        assert res.status_code == 200
        assert res.data['count'] >= 1

    def test_listar_incluye_inactivos(self, auth_client, service):
        service.is_active = False
        service.save()
        res = auth_client.get('/api/admin/services/')
        ids = [s['id'] for s in res.data['results']]
        assert service.id in ids

    def test_crear_servicio(self, auth_client, service_type, barber):
        data = {
            'name': 'Fade Premium',
            'description': 'Fade con degradado',
            'short_description': 'Fade',
            'price': '25.00',
            'duration': 45,
            'service_type': service_type.id,
            'is_active': True,
            'barber_ids': [barber.id]
        }
        res = auth_client.post('/api/admin/services/', data, format='json')
        assert res.status_code == 201
        assert res.data['name'] == 'Fade Premium'

    def test_crear_servicio_sin_barbers(self, auth_client, service_type):
        data = {
            'name': 'Servicio Sin Barbero',
            'description': 'Desc',
            'short_description': 'Desc corta',
            'price': '10.00',
            'duration': 20,
            'service_type': service_type.id,
            'is_active': True,
            'barber_ids': []
        }
        res = auth_client.post('/api/admin/services/', data, format='json')
        assert res.status_code == 201

    def test_patch_parcial_sin_barber_ids(self, auth_client, service):
        # PATCH sin barber_ids no debe fallar (required=False)
        res = auth_client.patch(
            f'/api/admin/services/{service.id}/',
            {'price': '20.00'},
            format='json'
        )
        assert res.status_code == 200
        assert res.data['price'] == '20.00'

    def test_actualizar_servicio_completo(self, auth_client, service, barber):
        data = {
            'name': 'Corte Actualizado',
            'description': 'Nueva descripción',
            'short_description': 'Nuevo corte',
            'price': '18.00',
            'duration': 35,
            'service_type': service.service_type.id,
            'is_active': True,
            'barber_ids': [barber.id]
        }
        res = auth_client.put(
            f'/api/admin/services/{service.id}/',
            data,
            format='json'
        )
        assert res.status_code == 200

    def test_eliminar_servicio(self, auth_client, service):
        res = auth_client.delete(f'/api/admin/services/{service.id}/')
        assert res.status_code == 204

    def test_filtrar_por_estado_activo(self, auth_client, service):
        res = auth_client.get('/api/admin/services/?is_active=true')
        assert res.status_code == 200

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/services/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestServiceTypes:

    def test_listar_tipos(self, auth_client, service_type):
        res = auth_client.get('/api/admin/services/types/')
        assert res.status_code == 200

    def test_crear_tipo(self, auth_client):
        res = auth_client.post('/api/admin/services/types/', {
            'name': 'Tratamiento',
            'description': 'Tratamientos capilares',
            'display_order': 3
        })
        assert res.status_code == 201

    def test_actualizar_tipo(self, auth_client, service_type):
        res = auth_client.patch(
            f'/api/admin/services/types/{service_type.id}/',
            {'display_order': 5},
            format='json'
        )
        assert res.status_code == 200

    def test_eliminar_tipo_sin_servicios(self, auth_client):
        from apps.services.models import ServiceType
        tipo_vacio = ServiceType.objects.create(
            name='Tipo Vacío',
            display_order=99
        )
        res = auth_client.delete(f'/api/admin/services/types/{tipo_vacio.id}/')
        assert res.status_code == 204

    def test_eliminar_tipo_con_servicios_falla(self, auth_client, service_type, service):
        res = auth_client.delete(f'/api/admin/services/types/{service_type.id}/')
        assert res.status_code == 400