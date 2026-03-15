from django.db.models import Count, Q

def auto_assign_barber(date, time, total_duration):
    """
    Asigna automáticamente el barbero con menos citas ese día
    entre los barberos disponibles para ese slot.

    Estrategia: balance de carga → el barbero menos ocupado recibe la cita.
    """

    from apps.barbers.models import Barber
    from .availability import is_slot_available

    # Obtener todos los barberos activos
    active_barbers = Barber.objects.filter(status__name='Activo')

    if not active_barbers.exists():
        return None

    # Filtrar barberos disponibles para ese slot
    available_barbers = []
    for barber in active_barbers:
        if is_slot_available(date, time, total_duration, barber.id):
            available_barbers.append(barber.id)

    if not available_barbers:
        return None

    # De los disponibles, elegir el que tenga menos citas ese día
    barber = Barber.objects.filter(
        id__in=available_barbers
    ).annotate(
        citas_hoy=Count(
            'appointments',
            filter=Q(appointments__date=date)
        )
    ).order_by('citas_hoy').first()

    return barber