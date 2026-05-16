from django.urls import path
from . import views

urlpatterns = [
    # ============ PAGE URLs ============
    # Homepage
    path('', views.home, name='home'),
    path('index.html', views.home, name='home_html'),
    
    # Booking Page
    path('booking/', views.booking_page, name='booking_page'),
    path('booking.html', views.booking_page, name='booking_page_html'),
    
    # Admin Dashboard - Multiple formats for convenience
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard_underscore'),
    path('admin-dashboard.html', views.admin_dashboard, name='admin_dashboard_html'),
    path('admin_dashboard.html', views.admin_dashboard, name='admin_dashboard_html_underscore'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    # Admin Login
    path('admin-login/', views.admin_login_page, name='admin_login_page'),
    path('admin-login.html', views.admin_login_page, name='admin_login_page_html'),
    path('admin-login/submit/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    
    # ============ API URLs ============
    # Bookings API
    path('api/bookings/', views.get_bookings_api, name='get_bookings'),
    path('api/bookings/create/', views.create_booking_api, name='create_booking'),
    path('api/bookings/<str:booking_id>/', views.get_booking_detail_api, name='get_booking_detail'),
    path('api/bookings/<str:booking_id>/update/', views.update_booking_api, name='update_booking'),
    path('api/bookings/<str:booking_id>/delete/', views.delete_booking_api, name='delete_booking'),
    
    # Statistics and Analytics
    path('api/stats/', views.get_stats_api, name='stats'),
    path('api/chart-data/', views.get_chart_data_api, name='chart_data'),
    path('api/service-price/<str:service_type>/', views.get_service_price_api, name='service_price'),
]