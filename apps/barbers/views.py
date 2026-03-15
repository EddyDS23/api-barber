from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from utils.permissions import AllowAny, IsAdmin
from .models import Barber, Specialty, BarberStatus
from .serializers import (
    BarberPublicSerializer,
    BarberAdminSerializer,
    SpecialtySerializer, 
    BarberStatusSerializer,
    SpecialtyAdminSerializer
    )
# Create your views here.


# ============================================
# VIEWS PÚBLICAS 
# ============================================

@extend_schema_view(
    list=extend_schema(
        tags=['Public - Team'],
        summary='Listar Barberos Activos',
        description='Retornar todos los barberos con estatus activos'
    ),
    retrieve=extend_schema(
        tags=['Public - Team'],
        summary='Detalle de un barbero',
        description='Retorna el detalle de un barbero específico.'
    )
)
class BarberPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura (list y retrieve).
    No permite crear, editar ni borrar desde este endpoint.
    Solo muestra barberos con status 'Activo'.
    """

    serializer_class = BarberPublicSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'nickname']
    ordering_fields = ['name']
    ordering = ['name']

    def get_queryset(self):
        return Barber.objects.filter(
            status__name = 'Activo'
        ).prefetch_related(
            'specialties'
        )
    

# ============================================
# VIEWS ADMIN 
# ============================================

@extend_schema_view(
    list=extend_schema(
        tags=['Admin - Barbers'],
        summary='Listar todos los barberos',
        description='Retorna todos los barberos sin filtro de estado. Requiere JWT.'
    ),
    retrieve=extend_schema(
        tags=['Admin - Barbers'],
        summary='Detalle de un barbero'
    ),
    create=extend_schema(
        tags=['Admin - Barbers'],
        summary='Crear barbero'
    ),
    update=extend_schema(
        tags=['Admin - Barbers'],
        summary='Actualizar barbero completo'
    ),
    partial_update=extend_schema(
        tags=['Admin - Barbers'],
        summary='Actualizar barbero parcial'
    ),
    destroy=extend_schema(
        tags=['Admin - Barbers'],
        summary='Eliminar barbero'
    ),
)
class BarberAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de barberos para el panel admin.
    Requiere JWT + is_staff=True
    """

    serializer_class = BarberAdminSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields=['name','nickname','email','phone']
    ordering_fields=['name','created_at']
    ordering=['name']
    parser_classes= [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = Barber.objects.select_related(
            'status'
        ).prefetch_related('specialties')

        status_name = self.request.query_params.get('status')
        if status_name:
            queryset = queryset.filter(status__name = status_name)
        
        return queryset
    
    @extend_schema(
        tags=['Admin - Barbers'],
        summary='Subir avatar del barbero',
        description='Sube o reemplaza la foto de perfil del barbero en Cloudinary.',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'avatar': {
                        'type': 'string',
                        'format': 'binary',  # ← esto hace que Swagger muestre el campo de archivo
                        'description': 'Imagen de perfil (JPG, PNG, máx 5MB)'
                    }
                },
                'required': ['avatar']
            }
        },
        responses={
            200: OpenApiResponse(description='Avatar actualizado correctamente'),
            400: OpenApiResponse(description='No se proporcionó imagen'),
        }
    )
    @action(
        detail=True,
        methods=['post'],
        url_path='upload-avatar',
        parser_classes=[MultiPartParser]
    )
    def upload_avatar(self, request, pk=None):
        """
        POST /api/admin/barbers/{id}/upload-avatar/
        Recibe: multipart/form-data con campo 'avatar'
        """

        barber = self.get_object()
        avatar = request.FILES.get('avatar')

        if not avatar:
            return Response(
                {'error':'No se proporciono ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        barber.avatar = avatar
        barber.save()

        return Response({
            'message':'Avatar actualizado correctamente',
            'avatar_url': barber.avatar.url
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=['Admin - Barbers'],
        summary='Estadísticas de barberos',
        description='Retorna conteo de barberos por estado.'
    )
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self,request):
        """
        GET /api/admin/barbers/stats/
        Retorna cuántos barberos hay por estado.
        """

        from django.db.models import Count
        stats = BarberStatus.objects.annotate(
            count=Count('barber')
        ).values('name','color_code','count')

        return  Response(list(stats))
    

@api_view(['GET'])
@permission_classes([IsAdmin])
@extend_schema(
    tags=['Admin - Barbers'],
    summary='Listar especialidades',
    description='Retorna todas las especialidades disponibles.'
)
def specialty_list(request):
    """
    GET /api/admin/barbers/specialties/
    """
    specialties = Specialty.objects.all().order_by('name')
    serializer = SpecialtySerializer(specialties, many=True)
    return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Admin - Barbers - Specialties'],
        summary='Listar especialidades'
    ),
    retrieve=extend_schema(
        tags=['Admin - Barbers - Specialties'],
        summary='Detalle de una especialidad'
    ),
    create=extend_schema(
        tags=['Admin - Barbers - Specialties'],
        summary='Crear especialidad'
    ),
    update=extend_schema(
        tags=['Admin - Barbers - Specialties'],
        summary='Actualizar especialidad completa'
    ),
    partial_update=extend_schema(
        tags=['Admin - Barbers - Specialties'],
        summary='Actualizar especialidad parcial'
    ),
    destroy=extend_schema(
        tags=['Admin - Barbers - Specialties'],
        summary='Eliminar especialidad'
    ),
)
class SpecialtyAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de especialidades.
    Requiere JWT + is_staff=True
    """
    serializer_class = SpecialtyAdminSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    def get_queryset(self):
        return Specialty.objects.all()

    def destroy(self, request, *args, **kwargs):
        """
        Verifica que la especialidad no tenga barberos asociados
        antes de eliminarla.
        """
        specialty = self.get_object()
        if specialty.barbers.exists():
            return Response(
                {
                    'error': f'No se puede eliminar "{specialty.name}" '
                             f'porque tiene barberos asociados. '
                             f'Desasigna la especialidad de esos barberos primero.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
