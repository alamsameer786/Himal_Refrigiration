from django.db import models


class Booking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    SERVICE_CHOICES = [

        # AC SERVICES
        ('AC Repair', 'AC Repair'),
        ('AC Servicing', 'AC Servicing'),
        ('AC Installation', 'AC Installation'),
        ('AC Uninstallation', 'AC Uninstallation'),
        ('AC Gas Filling', 'AC Gas Filling'),
        ('Split AC Service', 'Split AC Service'),
        ('Window AC Service', 'Window AC Service'),

        # REFRIGERATOR
        ('Refrigerator Repair', 'Refrigerator Repair'),
        ('Deep Freezer Repair', 'Deep Freezer Repair'),
        ('Commercial Freezer Repair', 'Commercial Freezer Repair'),

        # CHILLER
        ('Chiller Repair', 'Chiller Repair'),
        ('Cold Room Repair', 'Cold Room Repair'),
        ('Cold Storage Repair', 'Cold Storage Repair'),

        # WASHING MACHINE
        ('Washing Machine Repair', 'Washing Machine Repair'),
        ('Washing Machine Installation', 'Washing Machine Installation'),

        # WATER COOLER
        ('Water Cooler Repair', 'Water Cooler Repair'),
        ('Water Dispenser Repair', 'Water Dispenser Repair'),

        # GEYSER
        ('Geyser Repair', 'Geyser Repair'),
        ('Geyser Installation', 'Geyser Installation'),

        # OVEN & KITCHEN
        ('Microwave Oven Repair', 'Microwave Oven Repair'),
        ('Electric Oven Repair', 'Electric Oven Repair'),
        ('Induction Repair', 'Induction Repair'),

        # VEHICLE AC
        ('Vehicle AC Repair', 'Vehicle AC Repair'),
        ('Vehicle AC Gas Filling', 'Vehicle AC Gas Filling'),

        # OTHER SERVICES
        ('Fan Repair', 'Fan Repair'),
        ('Inverter Repair', 'Inverter Repair'),
        ('Stabilizer Repair', 'Stabilizer Repair'),
        ('LED TV Repair', 'LED TV Repair'),

    ]

    # PRICING ACCORDING TO NEPALI MARKET
    SERVICE_PRICES = {

        # AC
        'AC Repair': 2500,
        'AC Servicing': 1800,
        'AC Installation': 3500,
        'AC Uninstallation': 2000,
        'AC Gas Filling': 4500,
        'Split AC Service': 2200,
        'Window AC Service': 1800,

        # FRIDGE
        'Refrigerator Repair': 2800,
        'Deep Freezer Repair': 4000,
        'Commercial Freezer Repair': 5500,

        # CHILLER
        'Chiller Repair': 6500,
        'Cold Room Repair': 12000,
        'Cold Storage Repair': 18000,

        # WASHING MACHINE
        'Washing Machine Repair': 2500,
        'Washing Machine Installation': 1500,

        # WATER COOLER
        'Water Cooler Repair': 2200,
        'Water Dispenser Repair': 1800,

        # GEYSER
        'Geyser Repair': 2500,
        'Geyser Installation': 3000,

        # OVEN
        'Microwave Oven Repair': 2200,
        'Electric Oven Repair': 3500,
        'Induction Repair': 1500,

        # VEHICLE AC
        'Vehicle AC Repair': 4500,
        'Vehicle AC Gas Filling': 3500,

        # OTHER
        'Fan Repair': 1000,
        'Inverter Repair': 5000,
        'Stabilizer Repair': 1800,
        'LED TV Repair': 4500,
    }

    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('eSewa', 'eSewa'),
        ('Fonepay', 'Fonepay'),
        ('Card', 'Debit/Credit Card'),
    ]

    booking_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    full_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)

    email = models.EmailField(blank=True, null=True)

    address = models.TextField()

    city = models.CharField(max_length=100, null=True, blank=True)

    service_type = models.CharField(
        max_length=100,
        choices=SERVICE_CHOICES
    )

    preferred_date = models.DateField()
    preferred_time = models.CharField(max_length=50, blank=True, null=True, help_text="Preferred time slot (e.g., Morning, Afternoon)")


    problem_description = models.TextField(
        blank=True,
        null=True
    )

    price = models.IntegerField(default=0)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='Cash'
    )

    payment_status = models.CharField(
        max_length=20,
        default='Pending'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    technician_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    technician_phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    technician_notes = models.TextField(
        blank=True,
        null=True
    )

    customer_feedback = models.TextField(
        blank=True,
        null=True
    )

    rating = models.IntegerField(
        blank=True,
        null=True
    )

    is_emergency = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # AUTO GENERATE BOOKING ID
    def generate_booking_id(self):

        last_booking = Booking.objects.all().order_by('-id').first()

        if last_booking and last_booking.booking_id:

            try:
                last_num = int(
                    last_booking.booking_id.replace('HR-', '')
                )

                new_num = last_num + 1

            except:
                new_num = 1001

        else:
            new_num = 1001

        return f'HR-{new_num}'

    # SAVE METHOD
    def save(self, *args, **kwargs):

        if not self.booking_id:
            self.booking_id = self.generate_booking_id()

        # AUTO SET PRICE
        self.price = self.SERVICE_PRICES.get(
            self.service_type,
            0
        )

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.booking_id} | {self.full_name} | {self.service_type}"

    class Meta:

        ordering = ['-created_at']

        verbose_name = 'Booking'

        verbose_name_plural = 'Bookings'