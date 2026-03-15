from datetime import datetime, timedelta
from apps.core.models import BusinessHours, BusinessSettings, Holiday

def get_business_hours_for_date(date):
    """
    Retorna los horarios de apertura y cierre para una fecha dada.
    Retorna None si el negocio no trabaja ese día (feriado o día cerrado).
    """

    #Verificar si es dia feriado
    if Holiday.objects.filter(date=date).exists():
        return None
    

    #Convertir weekday de Python a nuestro formato
    # Python: 0=Lunes, 6=Domingo
    # Nuestro schema: 0=Domingo, 1=Lunes, ..., 6=Sábado

    python_weekday = date.weekday()
    if python_weekday == 6:
        day_of_week = 0
    else:
        day_of_week = python_weekday + 1


    #Buscar horario del dia
    try:
        
        hours = BusinessHours.objects.get(day_of_week=day_of_week)
        if not hours.is_working:
            return None
        
        return {
            'opening': hours.opening_time,
            'closing': hours.closing_time
        }

    except BusinessHours.DoesNotExist:
        return None
    
def is_slot_available(date, slot_time, total_duration, barber_id=None):
    """
    Verifica si un slot de tiempo está disponible.

    Un slot está ocupado si existe una cita que se traslapa con él.
    Ejemplo: cita a las 10:00 de 60 min ocupa hasta las 11:00,
    por lo tanto el slot de las 10:30 también está ocupado.
    """

    from .models import Appointment

    slot_start = datetime.combine(date, slot_time)
    slot_end = slot_start + timedelta(minutes=total_duration)

    # Buscar citas activas que se traslapen con el slot
    # Una cita se traslapa si:
    # - Empieza antes de que termine nuestro slot Y
    # - Termina después de que empiece nuestro slot

    active_status = ['Pendiente','Confirmada','En progreso']

    appointments = Appointment.objects.filter(
        date=date,
        status__name__in=active_status
    ) 

    if barber_id:
        appointments = Appointment.objects.filter(barber_id=barber_id)
    
    for appointment in appointments:
        apt_start = datetime.combine(date, appointment.time)
        apt_end = apt_start + timedelta(minutes=appointment.total_duration)
    

        if apt_start < slot_end and apt_end > slot_start:
            return False
        
    return True


def get_available_slots(date, service_ids, barber_id=None):
    """
    Retorna todos los slots disponibles para una fecha,
    lista de servicios y barbero opcional.

    Args:
        date: fecha de la cita (objeto date)
        service_ids: lista de IDs de servicios
        barber_id: ID del barbero (opcional)

    Returns:
        dict con date y lista de available_times
    """
     
    from apps.services.models import Service

    #1. Verificamos horarios del negocio
    bussiness_hours = get_business_hours_for_date(date)
    if not bussiness_hours:
        return {
            'date':str(date),
            'available_times':[],
            'message':'El negocio no opera este dia.'
        }
    
    #2. Calcular el total de tiempo en todos los servicios seleccionados
    services = Service.objects.filter(id__in=service_ids, is_active=True)
    if not services.exists():
        return {
            'date':str(date),
            'available_times':[],
            'message':'Los servicios seleccionados no son validos'
        }
    
    total_duration = sum(s.duration for s in services)

    #3.Obtener duracion del slot desde configuraciones (default 30min)
    try:
        settings = BusinessSettings.objects.get(id=1)
        slot_duration = settings.time_slot_duration
    except BusinessSettings.DoesNotExist:
        slot_duration = 30
    

    #4. Generar todos los slot posibles dentro del horario
    opening = datetime.combine(date, bussiness_hours['opening'])
    closing = datetime.combine(date, bussiness_hours['closing'])

    available_times = []
    current = opening

    while current + timedelta(minutes=total_duration) <= closing:
        slot_time = current.time()

    
        #5. Verificar si el slot esta disponible
        if is_slot_available(date, slot_time, total_duration, barber_id):
            available_times.append(slot_time.strftime('%H:%M'))
        
        current += timedelta(minutes=slot_duration)

    return {
        'date':str(date),
        'available_times':available_times
    }

        