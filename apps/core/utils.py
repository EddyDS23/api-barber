# apps/core/utils.py

import datetime
from decimal import Decimal


def calc_percent_change(current: Decimal, previous: Decimal) -> int:
    """
    Retorna el % de cambio entre dos períodos como entero.
    Si el anterior es 0 y el actual > 0 → retorna 100.
    Si ambos son 0 → retorna 0.
    """
    if previous == 0:
        return 100 if current > 0 else 0
    change = ((current - previous) / previous) * 100
    return int(round(change))


def get_month_ranges():
    """
    Retorna (first_current, last_current, first_previous, last_previous).
    """
    today = datetime.date.today()

    first_current = today.replace(day=1)

    if today.month == 12:
        first_next = today.replace(year=today.year + 1, month=1, day=1)
    else:
        first_next = today.replace(month=today.month + 1, day=1)
    last_current = first_next - datetime.timedelta(days=1)

    if today.month == 1:
        first_previous = today.replace(year=today.year - 1, month=12, day=1)
    else:
        first_previous = today.replace(month=today.month - 1, day=1)

    last_previous = first_current - datetime.timedelta(days=1)

    return first_current, last_current, first_previous, last_previous