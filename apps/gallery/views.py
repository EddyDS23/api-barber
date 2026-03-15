from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter,OpenApiTypes
from drf_spectacular.openapi import OpenApiTypes
import drf_spectacular.openapi as openapi


from utils.permissions import AllowAny
from .models import Gallery, GalleryCategory
from .serializers import GalleryPublicSerializer, GalleryCategorySerializer

# Create your views here.
@extend_schema_view(
    list=extend_schema(
        tags=['Public - Gallery'],
        summary='Listar imagenes de galeria',
        description='Retornar todas las imagenes activas. Filtrable por categoria',
        parameters=[
            OpenApiParameter(   
                name='category',
                description='Slug de la categoria, Ejemplo: fades, cortes_clasicos, barbas,...',
                required=False,
                type=str
            )
        ]
    ),
    retrieve=extend_schema(
        tags=['Public - Gallery'],
        summary='Detalle de una imagen'
    )
)
class GalleryPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint público de galería.
    Permite filtrar por categoría usando el slug.
    Ejemplo: /api/public/gallery/?category=fades
    """
    serializer_class = GalleryPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Gallery.objects.filter(
            is_active=True
        ).select_related(
            'category','barber'
        ).order_by(
            'display_order','-created_at'
        )
    
        category_slug = self.request.query_params.get('category')
        if category_slug and category_slug != 'todos':
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset
    

    
    @extend_schema(
        tags=['Public - Gallery'],
        summary='Listar Categorias de Galeria',
        description='Retornar todas las categorias disponibles para filtrar la galeria'
    )
    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self,request):
        """
            GET /api/public/gallery/categories/
            Retorna las categorías para que el frontend
            pueda construir los botones de filtro.
        """

        categories = GalleryCategory.objects.all().order_by('display_order')
        serializer = GalleryCategorySerializer(categories, many=True)
        return Response(serializer.data)
    

# ============================================================
# ADMIN VIEWS
# ============================================================
from utils.permissions import IsAdmin
from .serializers import GalleryCategoryAdminSerializer, GalleryAdminSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(tags=['Admin - Category - Gallery'], summary='Listar categorías'),
    retrieve=extend_schema(tags=['Admin - Category - Gallery'], summary='Detalle de categoría'),
    create=extend_schema(tags=['Admin - Category - Gallery'], summary='Crear categoría'),
    update=extend_schema(tags=['Admin - Category - Gallery'], summary='Actualizar categoría'),
    partial_update=extend_schema(tags=['Admin - Category - Gallery'], summary='Actualizar categoría parcial'),
    destroy=extend_schema(tags=['Admin - Category - Gallery'], summary='Eliminar categoría'),
)
class GalleryCategoryAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = GalleryCategoryAdminSerializer
    queryset = GalleryCategory.objects.all().order_by('display_order', 'name')

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.images.exists():
            return Response(
                {'error': f'No se puede eliminar "{category.name}" porque tiene imágenes asociadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(tags=['Admin - Gallery'], summary='Listar imágenes'),
    retrieve=extend_schema(tags=['Admin - Gallery'], summary='Detalle de imagen'),
    create=extend_schema(tags=['Admin - Gallery'], summary='Crear imagen (sin foto)'),
    update=extend_schema(tags=['Admin - Gallery'], summary='Actualizar imagen'),
    partial_update=extend_schema(tags=['Admin - Gallery'], summary='Actualizar imagen parcial'),
    destroy=extend_schema(tags=['Admin - Gallery'], summary='Eliminar imagen'),
)
class GalleryAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = GalleryAdminSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'category__name', 'barber__name']
    ordering_fields = ['display_order', 'created_at']
    ordering = ['display_order', '-created_at']

    def get_queryset(self):
        return Gallery.objects.select_related(
            'category', 'barber'
        ).all()

    @extend_schema(
    tags=['Admin - Gallery'],
    summary='Subir imagen a Cloudinary',
    request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Imagen JPG, PNG o WEBP (máx 5MB)'
                    }
                },
                'required': ['image']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'image_url': {'type': 'string'}
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        """
        POST /api/admin/gallery/{id}/upload-image/
        Sube o reemplaza la imagen en Cloudinary.
        """
        gallery_item = self.get_object()
        image_file = request.FILES.get('image')

        if not image_file:
            return Response(
                {'error': 'No se proporcionó ninguna imagen.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response(
                {'error': 'Formato no permitido. Usa JPG, PNG o WEBP.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar tamaño (5MB)
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'La imagen no puede superar 5MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        gallery_item.image_url = image_file
        gallery_item.save()

        return Response({
            'success': True,
            'image_url': gallery_item.image_url.url
        })

     
    

