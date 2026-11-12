from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, time
from django.utils import timezone
from django.conf import settings


class UserRegistration(models.Model):
    username = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password later

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class OwnerRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    turf_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.full_name

class Turf(models.Model):
    owner = models.ForeignKey(OwnerRegistration, on_delete=models.CASCADE, related_name='turfs')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=200)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="turfs_images/")
    is_approved = models.BooleanField(default=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TimeSlot(models.Model): 
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name="time_slots")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Refund Requested', 'Refund Requested'),
        ('Approved', 'Approved'),  # Final approval status
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey('UserRegistration', on_delete=models.CASCADE)
    turf = models.ForeignKey('Turf', on_delete=models.CASCADE)
    booking_date = models.DateField()

    # Many-to-many relationship with slots
    slots = models.ManyToManyField(TimeSlot, related_name="bookings")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    refund_requested = models.BooleanField(default=False)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.turf.name} ({self.booking_date})"

    @property
    def refund_enabled(self):
        """
        Refund is allowed if:
        - Paid
        - Not already requested
        - Current time is before the booking end time
        """
        if self.payment_status != 'Paid' or self.refund_requested:
            return False

        slots = self.slots.all()
        if not slots:
            return False

        # Use the latest slot end time to block refund after booking ends
        last_slot = slots.order_by('end_time').last()
        booking_end_datetime = datetime.combine(self.booking_date, last_slot.end_time)

        # Make booking_end_datetime timezone-aware if using timezones
        if timezone.is_naive(booking_end_datetime):
            booking_end_datetime = timezone.make_aware(booking_end_datetime)

        return timezone.now() < booking_end_datetime

class Job(models.Model):
    JOB_TYPES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('internship', 'Internship'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
class JobApplication(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey('UserRegistration', on_delete=models.CASCADE, null=True, blank=True)  
    name = models.CharField(max_length=150)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} applied for {self.job.title}"



class Review(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        UserRegistration,   # ✅ use your custom user model here
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username if self.user else 'Unknown'} on {self.turf.name}"


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('cash', 'Cash'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='card')

    PAYMENT_STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Payment for Booking ID {self.booking.id} - {self.payment_status}"
    
    
class ContactMessage(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"