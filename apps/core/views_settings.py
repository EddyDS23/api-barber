# apps/core/views_settings.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiTypes


from utils.permissions import IsAdmin
from .models import BusinessSettings, BusinessHours, Holiday, NotificationSettings
from .serializers import (
    BusinessInfoSerializer,
    BookingRulesSerializer,
    BusinessHoursSerializer,
    HolidaySerializer,
    NotificationSettingsSerializer,
)

SETTINGS_TAG              = 'Admin - Settings'
SETTINGS_NOTIFICATION_TAG = 'Admin - Notification - Settings'
SETTINGS_HOLIDAY_TAG      = 'Admin - Holiday - Settings'
SETTINGS_RULES_TAG        = 'Admin - Rules - Settings'
SETTINGS_HOURS_TAG        = 'Admin - Hours - Settings'


# ─────────────────────────────────────────────────────────────
#  HELPERS: singletons
# ─────────────────────────────────────────────────────────────

def get_business_settings():
    """
    Retorna el registro singleton de BusinessSettings (id=1).
    Si no existe lo crea con valores por default.
    """
    obj, _ = BusinessSettings.objects.get_or_create(
        id=1,
        defaults={
            'business_name': 'Mi Barbería',
            'address':       'Sin dirección',
            'phone':         '000-0000',
        }
    )
    return obj


def get_notification_settings():
    """Singleton para NotificationSettings."""
    obj, _ = NotificationSettings.objects.get_or_create(id=1)
    return obj


# ═════════════════════════════════════════════════════════════
#  APARTADO 1: Información General
# ═════════════════════════════════════════════════════════════

class BusinessInfoView(APIView):
    """
    GET   /api/admin/settings/business-info/
    PATCH /api/admin/settings/business-info/
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=[SETTINGS_TAG],
        summary='Obtener información general del negocio',
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        settings   = get_business_settings()
        serializer = BusinessInfoSerializer(settings)
        return Response(serializer.data)

    @extend_schema(
        tags=[SETTINGS_TAG],
        summary='Actualizar información general del negocio',
        responses= {200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        request=BusinessInfoSerializer
    )
    def patch(self, request):
        settings   = get_business_settings()
        serializer = BusinessInfoSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadLogoView(APIView):
    """
    POST /api/admin/settings/upload-logo/
    Sube o reemplaza el logo del negocio en Cloudinary.
    """
    permission_classes = [IsAdmin]
    parser_classes     = [MultiPartParser, FormParser]

    @extend_schema(
        tags=[SETTINGS_TAG],
        summary='Subir o reemplazar el logo del negocio',
        responses= {200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'logo': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Imagen PNG, JPG o SVG (máx 5MB)'
                    }
                },
                'required': ['logo']
            }
        }
    )
    def post(self, request):
        logo_file = request.FILES.get('logo')

        if not logo_file:
            return Response(
                {'error': 'El archivo logo es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed_types = ['image/jpeg', 'image/png', 'image/svg+xml']
        if logo_file.content_type not in allowed_types:
            return Response(
                {'error': 'Formato no permitido. Usa PNG, JPG o SVG.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if logo_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'El logo no puede superar 5MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        settings = get_business_settings()

        try:
            settings.logo_url = logo_file
            settings.save()
        except Exception as e:
            return Response(
                {'error': f'Error al subir el logo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'message':  'Logo actualizado correctamente.',
            'logo_url': settings.logo_url.url
        })


# ═════════════════════════════════════════════════════════════
#  APARTADO 2: Reglas de Reservas
# ═════════════════════════════════════════════════════════════

class BookingRulesView(APIView):
    """
    GET   /api/admin/settings/booking-rules/
    PATCH /api/admin/settings/booking-rules/
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=[SETTINGS_RULES_TAG],
        summary='Obtener reglas de reservas y agendamiento',
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        settings   = get_business_settings()
        serializer = BookingRulesSerializer(settings)
        return Response(serializer.data)

    @extend_schema(
        tags=[SETTINGS_RULES_TAG],
        summary='Actualizar reglas de reservas y agendamiento',
        responses={200: OpenApiTypes.OBJECT},
        request=BookingRulesSerializer
    )
    def patch(self, request):
        settings   = get_business_settings()
        serializer = BookingRulesSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ═════════════════════════════════════════════════════════════
#  APARTADO 3a: Horarios de la semana
# ═════════════════════════════════════════════════════════════

class BusinessHoursView(APIView):
    """
    GET /api/admin/settings/business-hours/
    PUT /api/admin/settings/business-hours/
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=[SETTINGS_HOURS_TAG],
        summary='Obtener horarios de operación de la semana',
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        hours      = BusinessHours.objects.all().order_by('day_of_week')
        serializer = BusinessHoursSerializer(hours, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=[SETTINGS_HOURS_TAG],
        summary='Actualizar horarios de operación de toda la semana',
        responses={200: OpenApiTypes.OBJECT},
        request=BusinessHoursSerializer(many=True)
    )
    def put(self, request):
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Se esperaba un array de horarios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        errors  = []
        updated = []

        for item in request.data:
            day_of_week = item.get('day_of_week')

            if day_of_week is None:
                errors.append({'error': 'day_of_week es requerido en cada item.'})
                continue

            try:
                hours_obj = BusinessHours.objects.get(day_of_week=day_of_week)
            except BusinessHours.DoesNotExist:
                hours_obj = None

            serializer = BusinessHoursSerializer(hours_obj, data=item, partial=False)

            if serializer.is_valid():
                serializer.save()
                updated.append(serializer.data)
            else:
                errors.append({
                    'day_of_week': day_of_week,
                    'errors':      serializer.errors
                })

        if errors:
            return Response(
                {'errors': errors, 'updated': updated},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(updated)


class BusinessHoursDayView(APIView):
    """
    PATCH /api/admin/settings/business-hours/{day_of_week}/
    Actualiza un solo día. day_of_week: 0=Dom, 1=Lun ... 6=Sáb
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=[SETTINGS_HOURS_TAG],
        summary='Actualizar horario de un día específico de la semana',
        responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
        request=BusinessHoursSerializer
    )
    def patch(self, request, day_of_week):
        try:
            hours_obj = BusinessHours.objects.get(day_of_week=day_of_week)
        except BusinessHours.DoesNotExist:
            return Response(
                {'error': f'No existe horario para el día {day_of_week}.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BusinessHoursSerializer(hours_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ═════════════════════════════════════════════════════════════
#  APARTADO 3b: Días Feriados
# ═════════════════════════════════════════════════════════════

class HolidaysView(APIView):
    """
    GET  /api/admin/settings/holidays/
    POST /api/admin/settings/holidays/
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=[SETTINGS_HOLIDAY_TAG],
        summary='Listar todos los días feriados registrados',
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        holidays   = Holiday.objects.all().order_by('date')
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=[SETTINGS_HOLIDAY_TAG],
        summary='Registrar un nuevo día feriado',
        responses={201: OpenApiTypes.OBJECT},
        request=HolidaySerializer
    )
    def post(self, request):
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HolidayDeleteView(APIView):
    """
    DELETE /api/admin/settings/holidays/{id}/
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=[SETTINGS_HOLIDAY_TAG],
        summary='Eliminar un día feriado por ID',
        responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}
    )
    def delete(self, request, pk):
        try:
            holiday = Holiday.objects.get(pk=pk)
        except Holiday.DoesNotExist:
            return Response(
                {'error': 'Feriado no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        holiday.delete()
        return Response(
            {'message': 'Feriado eliminado correctamente.'},
            status=status.HTTP_200_OK
        )


# ═════════════════════════════════════════════════════════════
#  APARTADO 4: Notificaciones
# ═════════════════════════════════════════════════════════════

class NotificationSettingsView(APIView):
    """
    GET   /api/admin/settings/notifications/
    PATCH /api/admin/settings/notifications/
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=[SETTINGS_NOTIFICATION_TAG],
        summary='Obtener configuración de notificaciones automáticas',
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        settings   = get_notification_settings()
        serializer = NotificationSettingsSerializer(settings)
        return Response(serializer.data)

    @extend_schema(
        tags=[SETTINGS_NOTIFICATION_TAG],
        summary='Actualizar configuración de notificaciones automáticas',
        responses={200: OpenApiTypes.OBJECT},
        request=NotificationSettingsSerializer
    )
    def patch(self, request):
        settings   = get_notification_settings()
        serializer = NotificationSettingsSerializer(
            settings, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)