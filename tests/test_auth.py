# tests/test_auth.py
import pytest


@pytest.mark.django_db
class TestLogin:

    def test_login_usuario_activo_existe(self, api_client, admin_user):
        """Verifica que el usuario admin existe y tiene is_staff."""
        assert admin_user.is_staff is True
        assert admin_user.check_password('testpass123') is True
        def test_login_credenciales_invalidas(self, api_client, admin_user):
            res = api_client.post('/api/admin/auth/login/', {
                'username': 'admin',
                'password': 'wrongpassword'
            })
            assert res.status_code == 400

    def test_login_usuario_no_staff(self, api_client, regular_user):
        res = api_client.post('/api/admin/auth/login/', {
            'username': 'user',
            'password': 'testpass123'
        })
        assert res.status_code == 400

    def test_login_campos_vacios(self, api_client):
        res = api_client.post('/api/admin/auth/login/', {})
        assert res.status_code == 400


@pytest.mark.django_db
class TestMe:

    def test_me_autenticado(self, auth_client, admin_user):
        res = auth_client.get('/api/admin/auth/me/')
        assert res.status_code == 200
        assert res.data['username'] == 'admin'

    def test_me_sin_token(self, api_client):
        res = api_client.get('/api/admin/auth/me/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestLogout:

    def test_logout_sin_refresh_retorna_400(self, auth_client):
        """Verifica que logout sin token retorna 400."""
        res = auth_client.post('/api/admin/auth/logout/', {})
        assert res.status_code == 400

    def test_logout_sin_refresh_token(self, auth_client):
        res = auth_client.post('/api/admin/auth/logout/', {})
        assert res.status_code == 400\



@pytest.mark.django_db
class TestTokenFlow:

    def test_login_retorna_error_con_credenciales_invalidas(self, api_client, admin_user):
        """Verifica que credenciales wrongas devuelven 400."""
        res = api_client.post('/api/admin/auth/login/', {
            'username': 'admin',
            'password': 'WRONG'
        })
        assert res.status_code == 400

    def test_me_con_force_authenticate(self, auth_client, admin_user):
        """Verifica que el endpoint /me/ funciona con autenticación."""
        res = auth_client.get('/api/admin/auth/me/')
        assert res.status_code == 200
        assert res.data['username'] == 'admin'

    def test_acceso_sin_token_retorna_401(self, api_client):
        res = api_client.get('/api/admin/auth/me/')
        assert res.status_code == 401
