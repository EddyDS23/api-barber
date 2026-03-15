from django.db import models
from cloudinary.models import CloudinaryField
from apps.barbers.models import Barber

# Create your models here.
class GalleryCategory(models.Model):
    """
    Tabla: gallery_categories
    Categorías: Todos, Fades, Cortes Clásicos, Barbas
    """

    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='gallery_categories'
        verbose_name='Categoria de Galeria'
        verbose_name_plural='Categorias de Galeria'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
    

class Gallery(models.Model):
    """
    Tabla: gallery
    Imágenes de trabajos realizados en la barbería
    """

    title = models.CharField(max_length=100, blank=True, null=True)
    image_url = CloudinaryField('gallery_name')
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.RESTRICT,
        db_column='category_id',
        related_name='images'
    )
    barber= models.ForeignKey(
        Barber,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='barber_id',
        related_name='gallery_images'
    )
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gallery'
        verbose_name = 'Imagen de Galeria'
        verbose_name_plural = 'Imagenes de Galeria'
        ordering = ['display_order','created_at']

    def __str__(self):
        return self.title or f"Image #{self.id}"
    