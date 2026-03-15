from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse


from backend.utils.permissions import AllowAny, IsAdmin
from .models import Service, ServiceType
from .serializers import ServicePublicSerializer, ServiceAdminSerializer, ServiceTypeSerializer, ServiceTypeAdminSerializer


# ============================================
# VIEWS PÚBLICAS ,
# ============================================


# Create your views here.
@extend_schema_view(
    list=extend_schema(
        tags=['Public - Services'],
        summary='Listar Servicios Activos',
        description='Retornar todos los servicios disponibles ordernados por tipos'
    ),
    retrieve=extend_schema(
        tags=['Public - Services'],
        summary='Detalle de un servicio',
        description='Retornar el detalle de un servicio especifico'
    )
)
class ServicePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Solo muestra servicios con is_active=True.
    Ordenados por tipo de servicio y nombre.
    """

    serializer_class = ServicePublicSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'short_description']
    ordering_fields = ['name','price', 'duration']

    def get_queryset(self):
        return Service.objects.filter(
            is_active = True
        ).select_related(
            'service_type'
        ).order_by(
            'service_type__display_order','name'
        )
    


# ============================================
# VIEWS ADMIN  
# ============================================

@extend_schema_view(
    list=extend_schema(
        tags=['Admin - Services'],
        summary='Listar todos los servicios',
        description='Retorna todos los servicios incluyendo inactivos. Requiere JWT.'
    ),
    retrieve=extend_schema(
        tags=['Admin - Services'],
        summary='Detalle de un servicio'
    ),
    create=extend_schema(
        tags=['Admin - Services'],
        summary='Crear servicio'
    ),
    update=extend_schema(
        tags=['Admin - Services'],
        summary='Actualizar servicio completo'
    ),
    partial_update=extend_schema(
        tags=['Admin - Services'],
        summary='Actualizar servicio parcial'
    ),
    destroy=extend_schema(
        tags=['Admin - Services'],
        summary='Eliminar servicio'
    ),
)
class ServiceAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de servicios para el panel admin.
    Requiere JWT + is_staff=True
    """
    serializer_class = ServiceAdminSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'short_description']
    ordering_fields = ['name','price','created_at']
    ordering = ['name']
    parser_classes = [MultiPartParser, FormParser, JSONParser]


    def get_queryset(self):
        queryset = Service.objects.select_related(
            'service_type'
        ).prefetch_related('barbers')

        # Filtro opcional por estado
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @extend_schema(
        tags=['Admin - Services'],
        summary='Subir imagen del servicio',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Imagen del servicio (JPG, PNG, máx 5MB)'
                    }
                },
                'required': ['image']
            }
        },
        responses={
            200: OpenApiResponse(description='Imagen actualizada correctamente'),
            400: OpenApiResponse(description='No se proporcionó imagen'),
        }
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='upload-image',
        parser_classes=[MultiPartParser]
    )
    def upload_image(self, request, pk=None):
        """
        POST /api/admin/services/{id}/upload-image/
        """
        service = self.get_object()
        image = request.FILES.get('image')

        if not image:
            return Response(
                {'error':'No se proporciono ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        service.image_url = image
        service.save()
        return Response({
            'message': 'Imagen actualizada correctamente.',
            'image_url': service.image_url.url
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdmin])
@extend_schema(
    tags=['Admin - Services'],
    summary='Listar tipos de servicios',
    description='Retorna todos los tipos de servicios disponibles.'
)
def service_type_list(request):
    """
    GET /api/admin/services/types/
    """
    types = ServiceType.objects.all().order_by('display_order')
    serializer = ServiceTypeSerializer(types, many=True)
    return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Admin - Types - Services'],
        summary='Listar tipos de servicios'
    ),
    retrieve=extend_schema(
        tags=['Admin - Types - Services'],
        summary='Detalle de un tipo de servicio'
    ),
    create=extend_schema(
        tags=['Admin - Types - Services'],
        summary='Crear tipo de servicio'
    ),
    update=extend_schema(
        tags=['Admin - Types - Services'],
        summary='Actualizar tipo de servicio completo'
    ),
    partial_update=extend_schema(
        tags=['Admin - Types - Services'],
        summary='Actualizar tipo de servicio parcial'
    ),
    destroy=extend_schema(
        tags=['Admin - Types - Services'],
        summary='Eliminar tipo de servicio'
    ),
)
class ServiceTypeAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de tipos de servicios.
    Requiere JWT + is_staff=True
    """
    serializer_class = ServiceTypeAdminSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['display_order', 'name']
    ordering = ['display_order']

    def get_queryset(self):
        return ServiceType.objects.all()

    def destroy(self, request, *args, **kwargs):
        """
        Verifica que el tipo no tenga servicios asociados
        antes de eliminarlo.
        """
        service_type = self.get_object()
        if service_type.services.exists():
            return Response(
                {
                    'error': f'No se puede eliminar "{service_type.name}" '
                             f'porque tiene servicios asociados. '
                             f'Reasigna o elimina esos servicios primero.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)