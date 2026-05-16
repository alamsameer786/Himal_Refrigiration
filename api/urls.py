from django.urls import path
from . import views

urlpatterns = [
    path('bookings/', views.booking_list, name='booking-list'),
    path('bookings/<str:booking_id>/status/', views.update_booking_status, name='update-status'),
    path('stats/', views.get_stats, name='stats'),
]