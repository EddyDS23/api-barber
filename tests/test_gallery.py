# tests/test_gallery.py
import pytest
from apps.gallery.models import Gallery, GalleryCategory


@pytest.fixture
def gallery_image(db, gallery_category, barber):
    return Gallery.objects.create(
        title='Fade Premium',
        category=gallery_category,
        barber=barber,
        display_order=1,
        is_active=True,
        image_url='https://res.cloudinary.com/test/image/upload/test.jpg'
    )


@pytest.mark.django_db
class TestGalleryCategoriesAdmin:

    def test_listar_categorias_admin(self, auth_client, gallery_category):
        res = auth_client.get('/api/admin/gallery/categories/')
        assert res.status_code == 200

    def test_crear_categoria(self, auth_client):
        res = auth_client.post('/api/admin/gallery/categories/', {
            'name': 'Barbas',
            'slug': 'barbas',
            'description': 'Trabajos de barba',
            'display_order': 2
        })
        assert res.status_code == 201
        assert res.data['name'] == 'Barbas'

    def test_crear_categoria_slug_duplicado_falla(self, auth_client, gallery_category):
        res = auth_client.post('/api/admin/gallery/categories/', {
            'name': 'Otro Nombre',
            'slug': gallery_category.slug  # duplicado
        })
        assert res.status_code == 400

    def test_actualizar_categoria(self, auth_client, gallery_category):
        res = auth_client.patch(
            f'/api/admin/gallery/categories/{gallery_category.id}/',
            {'display_order': 5},
            format='json'
        )
        assert res.status_code == 200

    def test_eliminar_categoria_sin_imagenes(self, auth_client):
        categoria_vacia = GalleryCategory.objects.create(
            name='Vacía',
            slug='vacia',
            display_order=99
        )
        res = auth_client.delete(
            f'/api/admin/gallery/categories/{categoria_vacia.id}/'
        )
        assert res.status_code == 204

    def test_eliminar_categoria_con_imagenes_falla(
        self, auth_client, gallery_category, gallery_image
    ):
        res = auth_client.delete(
            f'/api/admin/gallery/categories/{gallery_category.id}/'
        )
        assert res.status_code == 400
        assert 'imágenes' in res.data['error']

    def test_sin_jwt_retorna_401(self, api_client):
        res = api_client.get('/api/admin/gallery/categories/')
        assert res.status_code == 401


@pytest.mark.django_db
class TestGalleryImagesAdmin:

    def test_listar_imagenes_admin(self, auth_client, gallery_image):
        res = auth_client.get('/api/admin/gallery/images/')
        assert res.status_code == 200
        assert res.data['count'] >= 1

    def test_detalle_imagen(self, auth_client, gallery_image):
        res = auth_client.get(f'/api/admin/gallery/images/{gallery_image.id}/')
        assert res.status_code == 200
        assert res.data['title'] == 'Fade Premium'

    def test_crear_imagen(self, auth_client, gallery_category, barber):
        data = {
            'title': 'Nueva Imagen',
            'category': gallery_category.id,
            'barber': barber.id,
            'display_order': 2,
            'is_active': True,
            'image_url': 'https://res.cloudinary.com/test/image/upload/new.jpg'
        }
        res = auth_client.post('/api/admin/gallery/images/', data, format='json')
        assert res.status_code == 201

    def test_actualizar_imagen(self, auth_client, gallery_image):
        res = auth_client.patch(
            f'/api/admin/gallery/images/{gallery_image.id}/',
            {'is_active': False},
            format='json'
        )
        assert res.status_code == 200
        assert res.data['is_active'] is False

    def test_eliminar_imagen(self, auth_client, gallery_image):
        res = auth_client.delete(
            f'/api/admin/gallery/images/{gallery_image.id}/'
        )
        assert res.status_code == 204

    def test_imagen_inexistente_retorna_404(self, auth_client):
        res = auth_client.get('/api/admin/gallery/images/99999/')
        assert res.status_code == 404