from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from .models import Booking
import json
import logging

logger = logging.getLogger(__name__)

# ============ PAGE VIEWS ============

def home(request):
    """Homepage view"""
    return render(request, 'index.html')

def booking_page(request):
    """Booking page view"""
    return render(request, 'booking.html')

@ensure_csrf_cookie
def admin_login_page(request):
    """Admin login page with CSRF cookie"""
    return render(request, 'admin_login.html')

@login_required(login_url='/admin-login/')
def admin_dashboard(request):
    """Admin dashboard view (requires login)"""
    return render(request, 'admin_dashboard.html')

# ============ AUTHENTICATION VIEWS ============

@csrf_exempt
def admin_login(request):
    """Handle admin login - CSRF exempt for API calls"""
    if request.method == 'POST':
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except:
                username = request.POST.get('username')
                password = request.POST.get('password')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            auth_login(request, user)
            return JsonResponse({
                'success': True, 
                'redirect': '/admin-dashboard/'
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid username or password'
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def admin_logout(request):
    """Handle admin logout"""
    auth_logout(request)
    return redirect('/admin-login/')

# ============ API VIEWS - BOOKINGS ============

@csrf_exempt
@require_http_methods(["GET"])
def get_bookings_api(request):
    """Get all bookings with optional filters"""
    status_filter = request.GET.get('status', '')
    service_filter = request.GET.get('service', '')
    search = request.GET.get('search', '')
    
    bookings = Booking.objects.all()
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if service_filter:
        bookings = bookings.filter(service_type=service_filter)
    if search:
        bookings = bookings.filter(
            Q(full_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(booking_id__icontains=search)
        )
    
    data = []
    for booking in bookings:
        data.append({
            'id': booking.booking_id,
            'full_name': booking.full_name,
            'phone': booking.phone,
            'email': booking.email,
            'address': booking.address,
            'city': booking.city,
            'service_type': booking.service_type,
            'price': booking.price,
            'preferred_date': booking.preferred_date.strftime('%Y-%m-%d'),
            'preferred_time': booking.preferred_time.strftime('%H:%M') if booking.preferred_time else None,
            'problem_description': booking.problem_description,
            'payment_method': booking.payment_method,
            'payment_status': booking.payment_status,
            'status': booking.status,
            'technician_name': booking.technician_name,
            'technician_phone': booking.technician_phone,
            'technician_notes': booking.technician_notes,
            'customer_feedback': booking.customer_feedback,
            'rating': booking.rating,
            'is_emergency': booking.is_emergency,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': booking.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def create_booking_api(request):
    """Create a new booking"""
    if request.method == "OPTIONS":
        response = JsonResponse({'success': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        return response
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['full_name', 'phone', 'address', 'city', 'service_type', 'preferred_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False, 
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Validate phone number (Nepali format: 10 digits starting with 98 or 97)
        phone = data.get('phone', '')
        if not phone or not phone.isdigit() or len(phone) != 10:
            return JsonResponse({
                'success': False, 
                'error': 'Please enter a valid 10-digit Nepali phone number'
            }, status=400)
        
        # Handle time field - if it's a range, extract just the hour
        preferred_time = data.get('preferred_time', '')
        if preferred_time and ' - ' in preferred_time:
            # Extract just the start time (e.g., "03:00 PM" -> "15:00")
            time_part = preferred_time.split(' - ')[0].strip()
            # Convert to 24-hour format
            from datetime import datetime
            try:
                dt = datetime.strptime(time_part, '%I:%M %p')
                preferred_time = dt.strftime('%H:%M')
            except:
                preferred_time = '09:00'
        elif preferred_time and ':' in preferred_time:
            # Already in HH:MM format
            pass
        else:
            preferred_time = None
        
        # Create booking
        booking = Booking.objects.create(
            full_name=data.get('full_name'),
            phone=phone,
            email=data.get('email', ''),
            address=data.get('address'),
            city=data.get('city'),
            service_type=data.get('service_type'),
            preferred_date=data.get('preferred_date'),
            preferred_time=preferred_time,
            problem_description=data.get('problem_description', ''),
            payment_method=data.get('payment_method', 'Cash'),
            is_emergency=data.get('is_emergency', False)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Booking created successfully',
            'booking_id': booking.booking_id,
            'price': booking.price,
            'status': booking.status
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({
            'success': False, 
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def get_booking_detail_api(request, booking_id):
    """Get single booking details"""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        data = {
            'id': booking.booking_id,
            'full_name': booking.full_name,
            'phone': booking.phone,
            'email': booking.email,
            'address': booking.address,
            'city': booking.city,
            'service_type': booking.service_type,
            'price': booking.price,
            'preferred_date': booking.preferred_date.strftime('%Y-%m-%d'),
            'preferred_time': booking.preferred_time.strftime('%H:%M') if booking.preferred_time else None,
            'problem_description': booking.problem_description,
            'payment_method': booking.payment_method,
            'payment_status': booking.payment_status,
            'status': booking.status,
            'technician_name': booking.technician_name,
            'technician_phone': booking.technician_phone,
            'technician_notes': booking.technician_notes,
            'customer_feedback': booking.customer_feedback,
            'rating': booking.rating,
            'is_emergency': booking.is_emergency,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        return JsonResponse(data)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)

@csrf_exempt
@require_http_methods(["PUT", "OPTIONS"])
def update_booking_api(request, booking_id):
    """Update booking details"""
    if request.method == "OPTIONS":
        response = JsonResponse({'success': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'PUT, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        return response
    
    try:
        data = json.loads(request.body)
        booking = Booking.objects.get(booking_id=booking_id)
        
        # Update allowed fields
        allowed_fields = [
            'full_name', 'phone', 'email', 'address', 'city',
            'service_type', 'preferred_date', 'preferred_time',
            'problem_description', 'payment_method', 'payment_status',
            'status', 'technician_name', 'technician_phone',
            'technician_notes', 'is_emergency', 'customer_feedback', 'rating'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(booking, field, data[field])
        
        # If service type changed, price will auto-update on save
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Booking updated successfully',
            'booking_id': booking.booking_id,
            'price': booking.price,
            'status': booking.status
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Booking not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE", "OPTIONS"])
def delete_booking_api(request, booking_id):
    """Delete a booking"""
    if request.method == "OPTIONS":
        response = JsonResponse({'success': True})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'DELETE, OPTIONS'
        return response
    
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        booking.delete()
        return JsonResponse({
            'success': True, 
            'message': 'Booking deleted successfully'
        })
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Booking not found'
        }, status=404)

# ============ API VIEWS - STATISTICS & ANALYTICS ============

@csrf_exempt
@require_http_methods(["GET"])
def get_stats_api(request):
    """Get dashboard statistics"""
    total = Booking.objects.count()
    pending = Booking.objects.filter(status='Pending').count()
    confirmed = Booking.objects.filter(status='Confirmed').count()
    assigned = Booking.objects.filter(status='Assigned').count()
    in_progress = Booking.objects.filter(status='In Progress').count()
    completed = Booking.objects.filter(status='Completed').count()
    cancelled = Booking.objects.filter(status='Cancelled').count()
    
    # Revenue calculations
    total_revenue = Booking.objects.filter(status='Completed').aggregate(Sum('price'))['price__sum'] or 0
    pending_revenue = Booking.objects.filter(
        status__in=['Pending', 'Confirmed', 'Assigned', 'In Progress']
    ).aggregate(Sum('price'))['price__sum'] or 0
    
    # Today's bookings
    today = datetime.now().date()
    today_bookings = Booking.objects.filter(created_at__date=today).count()
    today_revenue = Booking.objects.filter(
        created_at__date=today, 
        status='Completed'
    ).aggregate(Sum('price'))['price__sum'] or 0
    
    # Emergency bookings
    emergency_count = Booking.objects.filter(
        is_emergency=True, 
        status__in=['Pending', 'Confirmed', 'Assigned']
    ).count()
    
    # Payment stats
    payment_breakdown = {
        'Cash': Booking.objects.filter(payment_method='Cash').count(),
        'eSewa': Booking.objects.filter(payment_method='eSewa').count(),
        'Fonepay': Booking.objects.filter(payment_method='Fonepay').count(),
        'Card': Booking.objects.filter(payment_method='Card').count(),
    }
    
    return JsonResponse({
        'total': total,
        'pending': pending,
        'confirmed': confirmed,
        'assigned': assigned,
        'in_progress': in_progress,
        'completed': completed,
        'cancelled': cancelled,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'today_bookings': today_bookings,
        'today_revenue': today_revenue,
        'emergency_count': emergency_count,
        'payment_breakdown': payment_breakdown
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_chart_data_api(request):
    """Get data for charts"""
    # Last 7 days bookings and revenue
    today = datetime.now().date()
    last_7_days = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = Booking.objects.filter(created_at__date=date).count()
        revenue = Booking.objects.filter(
            created_at__date=date, 
            status='Completed'
        ).aggregate(Sum('price'))['price__sum'] or 0
        last_7_days.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count,
            'revenue': revenue
        })
    
    # Service type distribution (top 10)
    service_distribution = {}
    for service, _ in Booking.SERVICE_CHOICES:
        count = Booking.objects.filter(service_type=service).count()
        if count > 0:
            service_distribution[service] = count
    
    # Sort by count and get top 10
    sorted_services = dict(sorted(service_distribution.items(), key=lambda x: x[1], reverse=True)[:10])
    
    return JsonResponse({
        'last_7_days': last_7_days,
        'service_distribution': sorted_services
    })

@csrf_exempt
@require_http_methods(["GET"])
def get_service_price_api(request, service_type):
    """Get price for a service type"""
    price = Booking.SERVICE_PRICES.get(service_type, 0)
    return JsonResponse({
        'price': price, 
        'currency': 'NPR',
        'service': service_type
    })

# ============ HELPER FUNCTION ============

def create_admin_user():
    """Create the admin user if it doesn't exist"""
    if not User.objects.filter(username='naushad').exists():
        User.objects.create_superuser(
            'naushad', 
            'himalrefrigiration@gmail.com', 
            'naushad@786'
        )
        print("✅ Admin user 'naushad' created successfully!")
    else:
        print("ℹ️ Admin user 'naushad' already exists.")