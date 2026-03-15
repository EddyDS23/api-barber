
from django.urls import path
from .views import AvailabilityView, BookAppointmentView, AppointmentStatusView

urlpatterns = [
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('status/', AppointmentStatusView.as_view(), name='appointment-status'),
]