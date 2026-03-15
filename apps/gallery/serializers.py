from rest_framework import serializers
from apps.barbers.models import Barber
from .models import Gallery, GalleryCategory


# ============================================================
# SERIALIZERS PUBLICOS
# ============================================================

class GalleryCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GalleryCategory
        fields = ['id','name','slug','description']


class GalleryPublicSerializer(serializers.ModelSerializer):

    """
    Serializer público de galería.
    Incluye la categoría y el barbero que realizó el trabajo.
    El campo image retorna la URL completa de Cloudinary.
    """

    category = GalleryCategorySerializer(read_only=True)
    barber_name = serializers.CharField(
        source='barber.name',
        read_only=True,
        default=None
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = [
            'id',
            'title',
            'image',
            'category',
            'barber_name',
            'display_order'
        ]

    def get_image(self,obj):
        if obj.image_url:
            return obj.image_url.url
        return None



# ============================================================
# ADMIN SERIALIZERS
# ============================================================

class GalleryCategoryAdminSerializer(serializers.ModelSerializer):
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = GalleryCategory
        fields = ['id', 'name', 'slug', 'description', 'display_order', 'image_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_image_count(self, obj):
        return obj.images.filter(is_active=True).count()


class GalleryAdminSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category_detail = GalleryCategorySerializer(source='category', read_only=True)
    barber_detail = serializers.SerializerMethodField()

    # Write fields
    category = serializers.PrimaryKeyRelatedField(
        queryset=GalleryCategory.objects.all(), write_only=True
    )
    barber = serializers.PrimaryKeyRelatedField(
        queryset=Barber.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Gallery
        fields = [
            'id', 'title', 'image', 'category', 'category_detail',
            'barber', 'barber_detail', 'display_order', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'image', 'created_at']

    def get_image(self, obj):
        if obj.image_url:
            return obj.image_url.url
        return None

    def get_barber_detail(self, obj):
        if obj.barber:
            return {'id': obj.barber.id, 'name': obj.barber.name}
        return None
