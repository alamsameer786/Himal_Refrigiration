from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_id', 'full_name', 'phone', 'service_type', 
        'price', 'status', 'payment_method', 'payment_status', 
        'preferred_date', 'is_emergency', 'created_at'
    ]
    
    list_filter = [
        'status', 'service_type', 'payment_method', 
        'payment_status', 'is_emergency', 'city'
    ]
    
    search_fields = [
        'booking_id', 'full_name', 'phone', 'email', 
        'address', 'technician_name'
    ]
    
    list_editable = ['status', 'payment_status']
    
    readonly_fields = [
        'booking_id', 'price', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Booking Information', {
            'fields': (
                'booking_id', 'full_name', 'phone', 'email',
                'address', 'city', 'service_type', 'problem_description'
            )
        }),
        ('Schedule', {
            'fields': ('preferred_date', 'preferred_time', 'is_emergency')
        }),
        ('Pricing & Payment', {
            'fields': ('price', 'payment_method', 'payment_status')
        }),
        ('Status & Assignment', {
            'fields': (
                'status', 'technician_name', 'technician_phone', 
                'technician_notes'
            )
        }),
        ('Customer Feedback', {
            'fields': ('customer_feedback', 'rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_emergency']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='Confirmed')
    mark_as_confirmed.short_description = "Mark selected bookings as Confirmed"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='Completed', payment_status='Paid')
    mark_as_completed.short_description = "Mark selected bookings as Completed"
    
    def mark_as_emergency(self, request, queryset):
        queryset.update(is_emergency=True)
    mark_as_emergency.short_description = "Mark selected as Emergency"