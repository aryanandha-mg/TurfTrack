from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ContactMessage
from datetime import datetime
from django.urls import reverse
from django.db.models import Q
import re
from .models import Job
import datetime
from .models import Turf, Booking,TimeSlot,JobApplication,Review, Payment
from .models import UserRegistration 
from .models import OwnerRegistration
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
User = get_user_model()


# Index
def index(request):
 
    return render(request, 'index.html')


def search_turf(request):
    query = request.GET.get('query', '')
    

    turfs = Turf.objects.all()

    # Filter by name/location
    if query:
        turfs = turfs.filter(Q(name__icontains=query) | Q(location__icontains=query))

    first_available_slot = {}

   
    context = {
        'turfs': turfs,
        'first_available_slot': first_available_slot,
        'query': query,
    }
    return render(request, 'home.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')

# Owner Registration


def owner_register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        turf_name = request.POST.get("turf_name")
        password = request.POST.get("password")

        # Check if email or phone already exists
        if OwnerRegistration.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register_owner')

        if OwnerRegistration.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number is already registered.")
            return redirect('register_owner')

        # Save owner with hashed password
        OwnerRegistration.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            turf_name=turf_name,
            password=password # ✅ hash password
        )

        messages.success(request, "Registered successfully! Please login.")
        return redirect('login_owner')  # ✅ Redirect to owner login page

    return render(request, 'register/owner-register.html')





# Owner Login

def login_owner(request):
    if request.method == "POST":
        username = request.POST.get("username")  # email
        password = request.POST.get("password")  # plain text

        try:
            owner = OwnerRegistration.objects.get(email=username)
        except OwnerRegistration.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login_owner')

        # Plain text password check
        if password == owner.password:
            # ✅ Check owner's status
            if owner.status == 'pending':
                messages.error(request, "Your account is pending approval by admin.")
                return redirect('login_owner')
            elif owner.status == 'rejected':
                messages.error(request, "Your account has been rejected by admin.")
                return redirect('login_owner')

            # ✅ Store owner session
            request.session['owner_id'] = owner.id
            request.session.set_expiry(3600)  # session expires in 1 hour
            messages.success(request, f"Welcome {owner.full_name}!")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login_owner')

    return render(request, 'login/owner-login.html')

# Logout

def logout_owner(request):
    request.session.pop('owner_id', None)  # safely clear session
    messages.success(request, "Logged out successfully!")
    return redirect('login_owner')




def owner_dashboard(request):
    # 1️⃣ Get owner_id from session
    owner_id = request.session.get('owner_id')
    if not owner_id:
        messages.error(request, "You need to log in first.")
        return redirect('login_owner')

    # 2️⃣ Fetch OwnerRegistration instance
    owner_profile = get_object_or_404(OwnerRegistration, id=owner_id)

    # 3️⃣ Fetch all turfs owned by this owner
    owner_turfs = Turf.objects.filter(owner=owner_profile)

    # 4️⃣ Fetch bookings for these turfs
    bookings = (
        Booking.objects.filter(turf__in=owner_turfs)
        .select_related('user', 'turf')
        .prefetch_related('slots')
        .order_by('-booked_at')
    )

    # 5️⃣ Fetch jobs posted by this owner
    # If OwnerRegistration.user exists, get jobs; else, get none
    jobs = Job.objects.filter(owner=owner_profile.user) if owner_profile.user else Job.objects.none()

    # 6️⃣ Fetch all applications for the owner's jobs
    applications = JobApplication.objects.filter(job__in=jobs).select_related('job', 'applicant').order_by('-applied_at')

    # 7️⃣ Fetch refund requests for this owner's turfs
    refund_requests = Booking.objects.filter(
    turf__in=owner_turfs,
    payment_status__in=['Refund Requested', 'Refund Approved']
    ).select_related('user', 'turf')
    # 8️⃣ Optional debug prints (remove in production)
    print("Owner:", owner_profile)
    print("Jobs:", list(jobs.values('id', 'title')))
    print("Applications:", list(applications.values('id', 'job_id', 'applicant_id', 'name')))

    # 9️⃣ Prepare context
    context = {
        'owner': owner_profile,
        'owner_turfs': owner_turfs,
        'bookings': bookings,
        'jobs': jobs,
        'applications': applications,
        'refund_requests': refund_requests,
    }

    return render(request, 'dashboard/owner-dashboard.html', context)





def owner_reviews(request):
    # 1️⃣ Get owner from session
    owner_id = request.session.get('owner_id')
    if not owner_id:
        messages.error(request, "You need to log in first.")
        return redirect('login_owner')

    owner_profile = get_object_or_404(OwnerRegistration, id=owner_id)

    # 2️⃣ Fetch all turfs owned by this owner
    owner_turfs = Turf.objects.filter(owner=owner_profile)

    # 3️⃣ Fetch reviews for these turfs
    reviews = Review.objects.filter(turf__in=owner_turfs).select_related('user', 'turf').order_by('-created_at')

    # 4️⃣ Render template
    context = {
        'owner': owner_profile,
        'reviews': reviews,
    }

    return render(request, 'owner-review.html', context)



def owner_booking_history(request, owner_id):
    # Get the owner dynamically or 404 if not found
    owner = get_object_or_404(OwnerRegistration, id=owner_id)

    # Get all turfs owned by this owner
    owner_turfs = Turf.objects.filter(owner=owner)

    # Get bookings only for these turfs
    bookings = Booking.objects.filter(
        turf__in=owner_turfs
    ).select_related('user', 'turf').prefetch_related('slots').order_by('-booking_date')

    context = {
        'bookings': bookings,
        'owner': owner
    }
    return render(request, 'owner_booking_history.html', context)
# admin login
# ---------------------

# Hardcoded admin credentials
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

def login_admin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            messages.success(request, "Welcome Admin!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login_admin')

    return render(request, 'login/admin-login.html')





def admin_dashboard(request):
    # Fetch all bookings with related user and turf
    bookings = Booking.objects.select_related('user', 'turf').prefetch_related('slots').order_by('-booked_at')
    
    # Fetch all reviews
    reviews = Review.objects.select_related('turf', 'user').order_by('-created_at')
    
    # Fetch all owners
    owners = OwnerRegistration.objects.all().order_by('-created_at')
    
    # Fetch all complaints
    complaints = ContactMessage.objects.all().order_by('-created_at')
    
    # Fetch all turfs for admin approval
    turfs = Turf.objects.select_related('owner').order_by('-created_at')  # include owner info
    
    print("Owners Data Sent to Template:", list(owners.values()))
    print("Turfs Data Sent to Template:", list(turfs.values()))
    
    return render(request, 'dashboard/admin-dashboard.html', {
        'bookings': bookings,
        'reviews': reviews,
        'owners': owners,
        'complaints': complaints,
        'turfs': turfs,  # send turfs to template
        
    })


 # Approve/Reject owner actions
def approve_owner(request, owner_id):
    owner = get_object_or_404(OwnerRegistration, id=owner_id)
    owner.status = 'approved'
    owner.save()
    return redirect('admin_dashboard')

def reject_owner(request, owner_id):
    owner = get_object_or_404(OwnerRegistration, id=owner_id)
    owner.status = 'rejected'
    owner.save()
    return redirect('admin_dashboard')


from django.http import JsonResponse

def approve_turf(request, status, turf_id):
    if request.method == "POST":
        turf = get_object_or_404(Turf, id=turf_id)
        if status in ['approved', 'rejected']:
            turf.status = status
            turf.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def reject_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.status = 'rejected'
    turf.save()
    return redirect('admin_dashboard')



def logout_admin(request):
    # Safely remove the admin session key
    request.session.pop('admin_logged_in', None)
    messages.success(request, "Logged out successfully!")
    return redirect('login_admin')

# USER REGISTER
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        phone = request.POST.get('phone').strip()

        # ---------- VALIDATIONS ----------
        # Username must only contain letters and spaces
        if not re.match(r'^[A-Za-z\s]+$', username):
            messages.error(request, "Username should contain only letters and spaces.")
            return redirect('register_user')

        # Email validation
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messages.error(request, "Invalid email format.")
            return redirect('register_user')

        # Phone number must be exactly 10 digits
        if not re.match(r'^\d{10}$', phone):
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect('register_user')

        # Password must have at least 8 characters and one special character
        if len(password) < 8 or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, "Password must be at least 8 characters and include a special character.")
            return redirect('register_user')

        # Check if username, email, or phone already exists
        if UserRegistration.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register_user')
        if UserRegistration.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register_user')
        if UserRegistration.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered.")
            return redirect('register_user')

        # ---------- SAVE USER ----------
        user = UserRegistration(
            username=username,
            email=email,
            phone=phone,
            password=make_password(password)  # Hash the password
        )
        user.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login_user')

    return render(request, 'register/user-register.html')


# USER LOGIN
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        try:
            user = UserRegistration.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id  # Store user ID in session
                messages.success(request, f"Welcome {user.username}!")
                return redirect('home')  # Redirect to home page
            else:
                messages.error(request, "Invalid password.")
        except UserRegistration.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, 'login/user-login.html')

# ---------------------
# LOGOUT
# ---------------------
def logout_user(request):
    logout(request)
    return redirect('login_user')



# ---------------------
# DASHBOARD VIEWS
# ---------------------
def user_dashboard(request):
    return render(request, 'dashboard/user-dashboard.html')



# Static pages

def home(request):
    #turfs = Turf.objects.all().order_by('-created_at')
    turfs = Turf.objects.filter(status='approved').order_by('-created_at')
    return render(request, 'home.html', {'turfs': turfs})


def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == "POST":
        # Capture form data
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save to the database
        ContactMessage.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            message=message
        )

        # Success message
        messages.success(request, "Your message has been sent successfully! We'll get back to you shortly.")
        return redirect('contact')  # reload the page
    return render(request, 'contact.html')




# ---------------------




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from .models import Turf, Booking, TimeSlot, UserRegistration

from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Turf, TimeSlot, Booking, UserRegistration

def book_now(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    today = datetime.today()
    week_days = [today + timedelta(days=i) for i in range(30)]  # Next 30 days

    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to book a slot.")
        return redirect('login_user')

    try:
        user_registration = UserRegistration.objects.get(id=user_id)
    except UserRegistration.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login_user')

    # Determine selected date from GET parameter or default to today
    booking_date_param = request.GET.get('booking_date')
    if booking_date_param:
        try:
            selected_day = datetime.strptime(booking_date_param, "%Y-%m-%d").date()
        except ValueError:
            selected_day = today.date()
    else:
        selected_day = today.date()

    if request.method == "POST":
        booking_date = request.POST.get('booking_date')
        slot_times_raw = request.POST.getlist('slot_time')  # multiple slots
        total_amount = request.POST.get('total_amount')

        slot_times = [int(s) for s in slot_times_raw] if slot_times_raw else []

        if not booking_date or not slot_times or not total_amount:
            messages.error(request, "Please select a date, slot(s), and amount before proceeding.")
            return redirect('book_now', turf_id=turf.id)

        # Check if any selected slots are already booked by this user and paid
        already_paid = Booking.objects.filter(
            turf=turf,
            booking_date=booking_date,
            status='paid',  # Only paid slots are unavailable
            slots__id__in=slot_times
        ).exists()

        if already_paid:
            messages.error(request, "One or more selected slots are already paid and unavailable!")
            return redirect('book_now', turf_id=turf.id)

        # Create a new booking (pending by default)
        booking = Booking.objects.create(
            user_id=user_id,
            user=user_registration, 
            turf=turf,
            booking_date=booking_date,
            total_amount=total_amount,
            status='pending'
        )
        booking.slots.set(slot_times)

        messages.success(request, "Booking created successfully! Redirecting to payment...")
        return redirect('payment', booking_id=booking.id)

    # GET request: show available slots
    # Include all slots and mark booked slots for this user as disabled
    booked_slots = Booking.objects.filter(
    turf=turf,
    booking_date=selected_day,  # only slots booked on selected date
    user_id=user_id  # current user's bookings
    ).values_list('slots__id', flat=True)

    available_slots = TimeSlot.objects.filter(turf=turf)

    return render(request, 'book-now.html', {
    'turf': turf,
    'available_slots': available_slots,
    'booked_slots': list(booked_slots),
    'week_days': week_days,
    'selected_day': selected_day,
})


from django.utils import timezone
from datetime import datetime

def booking_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to view booking history.")
        return redirect('login_user')

    custom_user = get_object_or_404(UserRegistration, id=user_id)
    bookings = Booking.objects.filter(user=custom_user).prefetch_related('slots').order_by('-booking_date')
    now = timezone.now()  # aware datetime

    for booking in bookings:
        booking.can_refund = False
        if booking.payment_status == 'Paid':
            for slot in booking.slots.all():
                # Combine date and time
                slot_datetime = datetime.combine(booking.booking_date, slot.start_time)
                # Make it timezone-aware using the current timezone
                slot_datetime = timezone.make_aware(slot_datetime, timezone.get_current_timezone())

                if slot_datetime > now:
                    booking.can_refund = True
                    break  # At least one future slot is enough

    return render(request, 'booking-history.html', {
        'bookings': bookings,
        'now': now
    })




def request_refund(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user__id=request.session.get('user_id'))

    # 1️⃣ Ensure refund is only for paid bookings
    if booking.payment_status != 'Paid':
        messages.error(request, "Refund can only be requested for paid bookings.")
        return redirect('booking_history')

    # 2️⃣ Check if refund already requested
    if booking.refund_requested:
        messages.info(request, "Refund already requested.")
        return redirect('booking_history')

    # 3️⃣ Check if any slot has already started
    now = timezone.now()
    for slot in booking.slots.all():
        slot_datetime = datetime.combine(booking.booking_date, slot.start_time)
        if slot_datetime <= now:
            messages.error(request, "Cannot request refund after the slot has started.")
            return redirect('booking_history')

    # 4️⃣ Mark refund requested
    booking.refund_requested = True
    booking.payment_status = 'Refund Requested'
    booking.save()

    messages.success(request, "Refund requested successfully!")
    return redirect('booking_history')



def approve_refund(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Ensure the logged-in owner owns this turf
    owner_id = request.session.get('owner_id')
    if booking.turf.owner.id != owner_id:
        messages.error(request, "You are not authorized to approve this refund.")
        return redirect('owner_dashboard')

    # Update booking status
    booking.payment_status = 'Refund Approved'
    booking.status = 'Cancelled'
    booking.save()

    messages.success(request, "Refund approved successfully!")
    return redirect('owner_dashboard')





def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    turf_name = booking.turf.name
    booking_date = booking.booking_date
    selected_slots = booking.slots.all()
    total_amount = booking.total_amount

    context = {
        'booking_id': booking.id,
        'turf': turf_name,
        'date': booking_date,
        'slots': selected_slots,
        'amount': total_amount,
    }
    return render(request, 'payment.html', context)




from django.contrib.auth.decorators import login_required


def confirm_payment(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        payment_method = request.POST.get("payment_method")

        # Get current logged-in custom user from session
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "User session expired. Please log in again.")
            return redirect('login_user')

        custom_user = get_object_or_404(UserRegistration, id=user_id)

        # Fetch booking for this user
        booking = get_object_or_404(Booking, id=booking_id, user=custom_user)

        # Capture payment fields
        if payment_method == "card":
            cardholder_name = request.POST.get("cardholder_name")
            card_number = request.POST.get("card_number")
            expiry = request.POST.get("expiry")
            cvv = request.POST.get("cvv")
        elif payment_method == "upi":
            upi_id = request.POST.get("upi_id")

        # Save payment record
        Payment.objects.create(
            booking=booking,
            amount_paid=booking.total_amount,
            payment_method=payment_method,
            payment_status="success"
        )

        # Update booking
        booking.status = "confirmed"
        booking.payment_status = "Paid"
        booking.save()

        messages.success(request, "Payment successful!")
        return redirect('booking_confirmation', booking_id=booking.id)
    else:
        messages.error(request, "Invalid request method.")
        return redirect('home')




def booking_confirmation(request, booking_id):
    try:
        user = UserRegistration.objects.get(id=request.session.get('user_id'))
    except UserRegistration.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login_user')

    booking = get_object_or_404(Booking, id=booking_id, user=user)
    return render(request, 'booking-confirmation.html', {'booking': booking})



def job(request):
    return render(request, 'job.html')

def job_list(request):
    # Fetch all jobs from the database
    jobs = Job.objects.all().order_by('-created_at')  # latest jobs first
    return render(request, 'job.html', {'jobs': jobs})


def apply_job(request):
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        resume = request.FILES.get('resume')

        job = get_object_or_404(Job, id=job_id)

        # If the user is logged in, link their UserRegistration record
        applicant = None
        if request.session.get('user_id'):
            applicant = get_object_or_404(UserRegistration, id=request.session['user_id'])

        JobApplication.objects.create(
            job=job,
            applicant=applicant,
            name=name,
            email=email,
            resume=resume
        )

        messages.success(request, "Your application has been submitted successfully!")
        return redirect('job')  # Redirect back to job listing

    return redirect('job')



def logout_owner(request):
    request.session.pop('owner_id', None)
    messages.success(request, "Logged out successfully!")
    return redirect('login_owner')







def add_turf(request):
    owner_id = request.session.get('owner_id')
    print("Session owner_id:", owner_id)  # Debugging

    if not owner_id:
        messages.error(request, "Please login as owner first.")
        return redirect('login_owner')

    owner = get_object_or_404(OwnerRegistration, id=owner_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        price_per_hour = request.POST.get('price_per_hour')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        from decimal import Decimal
        try:
            price_per_hour = Decimal(price_per_hour)
        except:
            messages.error(request, "Invalid price format.")
            return redirect('add_turf')

        # ✅ Create turf with status 'pending'
        turf = Turf.objects.create(
            owner=owner,
            name=name,
            location=location,
            price_per_hour=price_per_hour,
            description=description,
            image=image,
            status='pending'  # Turf will be pending until admin approves
        )

        messages.success(request, f"Turf '{turf.name}' submitted for approval! Admin will review it shortly.")
        return redirect('owner_dashboard')

    return render(request, 'add-turf.html')




def post_job(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        job_type = request.POST.get('job_type')
        salary = request.POST.get('salary')

        # Validation
        if not title or not description or not job_type or not salary:
            messages.error(request, "All fields are required.")
            return redirect('post_job')

        # Save job
        Job.objects.create(
            title=title,
            description=description,
            job_type=job_type,
            salary=salary,
            owner=request.user
        )
        messages.success(request, "Job posted successfully!")
        return redirect('owner_dashboard')  # Redirect after successful submission

    return render(request, 'post-job.html')  # Your template file

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Turf, OwnerRegistration

def manage_turf(request):
    owner_id = request.session.get('owner_id')

    if not owner_id:
        messages.error(request, "Please log in as an owner first.")
        return redirect('login_owner')

    owner = get_object_or_404(OwnerRegistration, id=owner_id)

    # ✅ Fetch all turfs of the owner (approved, pending, rejected)
    turfs = Turf.objects.filter(owner=owner).order_by('status', '-created_at')
    
    return render(request, 'manage-turf.html', {'turfs': turfs})

def edit_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':
        turf.name = request.POST.get('name')
        turf.location = request.POST.get('location')
        turf.price_per_hour = request.POST.get('price_per_hour')
        turf.description = request.POST.get('description')

        if request.FILES.get('image'):
            turf.image = request.FILES['image']  # Update image only if provided

        turf.save()
        messages.success(request, f"Turf '{turf.name}' updated successfully!")
        return redirect('manage_turf')

    return render(request, 'edit-turf.html', {'turf': turf})


def add_slot(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        # Save slot
        TimeSlot.objects.create(
            turf=turf,
            start_time=start_time,
            end_time=end_time
        )
        messages.success(request, f"Slot {start_time} - {end_time} added successfully!")
        return redirect('manage_turf')

    return render(request, 'add-slot.html', {'turf': turf})


def delete_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.delete()
    return redirect('manage_turf') 


def review(request):
    turfs = Turf.objects.all()  # For dropdown list of turfs

    # ✅ Get logged-in user from session
    user_id = request.session.get('user_id')
    user = None
    if user_id:
        try:
            user = UserRegistration.objects.get(id=user_id)
        except UserRegistration.DoesNotExist:
            user = None

    if request.method == "POST":
        turf_id = request.POST.get("turf_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not turf_id or not rating or not comment:
            messages.error(request, "All fields are required.")
            return redirect('review')

        # Ensure valid turf
        turf = get_object_or_404(Turf, id=turf_id)

        # If user not logged in
        if not user:
            messages.error(request, "You must be logged in to submit a review.")
            return redirect('login_user')

        # ✅ Save review with correct user
        Review.objects.create(
            turf=turf,
            user=user,
            rating=int(rating),
            comment=comment
        )

        messages.success(request, "Your review has been submitted successfully!")
        return redirect('review')

    # Fetch all reviews
    reviews = Review.objects.select_related('user', 'turf').order_by('-created_at')
    return render(request, 'review.html', {"reviews": reviews, "turfs": turfs})
        
