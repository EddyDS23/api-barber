# tests/test_barbers.py
import pytest


@pytest.mark.django_db
class TestBarbersCRUD:

    def test_listar_barberos(self, auth_client, barber):
        res = auth_client.get('/api/admin/barbers/')
        assert res.status_code == 200

    def test_crear_barbero(self, auth_client, barber_status_activo):
        data = {
            'name': 'Nuevo Barbero',
            'phone': '555-7777',
            'color_code': '#AABBCC',
            'status': barber_status_activo.id
        }
        res = auth_client.post('/api/admin/barbers/', data)
        assert res.status_code == 201
        assert res.data['name'] == 'Nuevo Barbero'

    def test_crear_barbero_color_invalido(self, auth_client, barber_status_activo):
        data = {
            'name': 'Barbero',
            'phone': '555-6666',
            'color_code': 'rojo',  # inválido
            'status': barber_status_activo.id
        }
        res = auth_client.post('/api/admin/barbers/', data)
        assert res.status_code == 400

    def test_actualizar_barbero(self, auth_client, barber):
        res = auth_client.patch(f'/api/admin/barbers/{barber.id}/', {
            'nickname': 'El Maestro'
        })
        assert res.status_code == 200
        assert res.data['nickname'] == 'El Maestro'

    def test_eliminar_barbero_sin_citas(self, auth_client, barber):
        res = auth_client.delete(f'/api/admin/barbers/{barber.id}/')
        assert res.status_code == 204

    def test_stats_barberos(self, auth_client, barber):
        res = auth_client.get('/api/admin/barbers/stats/')
        assert res.status_code == 200

    def test_sin_jwt_retorna_401(self, api_client, barber):
        res = api_client.get('/api/admin/barbers/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestSpecialties:

    def test_listar_especialidades(self, auth_client, specialty):
        res = auth_client.get('/api/admin/barbers/specialties/')
        assert res.status_code == 200

    def test_crear_especialidad(self, auth_client):
        res = auth_client.post('/api/admin/barbers/specialties/', {
            'name': 'Diseños',
            'description': 'Diseños artísticos'
        })
        assert res.status_code == 201

    def test_eliminar_especialidad_con_barberos_falla(
        self, auth_client, barber, specialty
    ):
        BarberSpecialty = __import__(
            'apps.barbers.models', fromlist=['BarberSpecialty']
        ).BarberSpecialty
        BarberSpecialty.objects.create(barber=barber, specialty=specialty)
        res = auth_client.delete(f'/api/admin/barbers/specialties/{specialty.id}/')
        assert res.status_code == 400