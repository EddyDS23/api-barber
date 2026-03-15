from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from backend.utils.permissions import IsAdmin
from .models import Client
from .serializers import ClientAdminSerializer, ClientCreateSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Admin - Clients'],
        summary='Listar clientes',
        description='Retorna todos los clientes con su última visita y total gastado.',
        parameters=[
            OpenApiParameter(
                name='search',
                description='Buscar por nombre o teléfono',
                required=False,
                type=str
            )
        ]
    ),
    retrieve=extend_schema(
        tags=['Admin - Clients'],
        summary='Detalle de un cliente'
    ),
    create=extend_schema(
        tags=['Admin - Clients'],
        summary='Crear cliente'
    ),
    update=extend_schema(
        tags=['Admin - Clients'],
        summary='Actualizar cliente completo'
    ),
    partial_update=extend_schema(
        tags=['Admin - Clients'],
        summary='Actualizar cliente parcial'
    ),
    destroy=extend_schema(
        tags=['Admin - Clients'],
        summary='Eliminar cliente'
    ),
)
class ClientAdminViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de clientes para el panel admin.
    Requiere JWT + is_staff=True
    """
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'phone', 'email']
    ordering_fields = ['full_name', 'created_at']
    ordering = ['full_name']

    def get_queryset(self):
        return Client.objects.prefetch_related(
            'appointments__status'
        ).all()

    def get_serializer_class(self):
        """
        Usa serializer simple para crear/editar
        y serializer completo para listar/ver.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ClientCreateSerializer
        return ClientAdminSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Verifica que el cliente no tenga citas activas
        antes de eliminarlo.
        """
        client = self.get_object()
        active_appointments = client.appointments.filter(
            status__name__in=['Pendiente', 'Confirmada', 'En progreso']
        )
        if active_appointments.exists():
            return Response(
                {
                    'error': f'No se puede eliminar a "{client.full_name}" '
                             f'porque tiene citas activas. '
                             f'Cancela o completa esas citas primero.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=['Admin - Clients'],
        summary='Historial de citas del cliente',
        description='Retorna todas las citas del cliente ordenadas por fecha.'
    )
    @action(detail=True, methods=['get'], url_path='appointments')
    def appointments(self, request, pk=None):
        """
        GET /api/admin/clients/{id}/appointments/
        Historial de citas del cliente.
        """
        from apps.appointments.models import Appointment

        client = self.get_object()
        appointments = Appointment.objects.filter(
            client=client
        ).select_related(
            'barber', 'status'
        ).prefetch_related(
            'appointmentservice_set__service'
        ).order_by('-date', '-time')

        data = [
            {
                'id': apt.id,
                'date': str(apt.date),
                'time': str(apt.time),
                'barber': apt.barber.name,
                'status': apt.status.name,
                'services': [
                    ap_service.service.name
                    for ap_service in apt.appointmentservice_set.all()
                ],
                'total_amount': str(apt.total_amount),
                'confirmation_code': apt.confirmation_code,
            }
            for apt in appointments
        ]

        return Response(data)