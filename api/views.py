from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from bookings.models import Booking
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@api_view(['GET', 'POST'])
def booking_list(request):
    if request.method == 'GET':
        bookings = Booking.objects.all()
        data = []
        for booking in bookings:
            data.append({
                'id': booking.booking_id,
                'full_name': booking.full_name,
                'phone': booking.phone,
                'address': booking.address,
                'service_type': booking.service_type,
                'preferred_date': booking.preferred_date.strftime('%Y-%m-%d'),
                'status': booking.status,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return Response(data)
    
    elif request.method == 'POST':
        try:
            data = request.data
            booking = Booking.objects.create(
                full_name=data['full_name'],
                phone=data['phone'],
                address=data['address'],
                service_type=data['service_type'],
                preferred_date=data['preferred_date']
            )
            return Response({
                'success': True,
                'message': 'Booking created successfully',
                'booking_id': booking.booking_id,
                'status': booking.status
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_booking_status(request, booking_id):
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        booking.status = request.data.get('status', booking.status)
        booking.save()
        return Response({
            'success': True,
            'message': 'Status updated successfully',
            'new_status': booking.status
        })
    except Booking.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_stats(request):
    total = Booking.objects.count()
    pending = Booking.objects.filter(status='Pending').count()
    confirmed = Booking.objects.filter(status='Confirmed').count()
    completed = Booking.objects.filter(status='Completed').count()
    
    return Response({
        'total': total,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed
    })