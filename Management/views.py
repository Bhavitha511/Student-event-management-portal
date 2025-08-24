from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import *
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.

def home(request):
    announcements = GlobalAnnouncement.objects.order_by('-created_at')[:5]  # latest 5
    return render(request, 'home.html', {'announcements': announcements})

#-----------------------------------------------------------------------------------------------------
def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def user_dashboard(request):
    user = request.user
    registrations = EventRegistration.objects.filter(user=user).select_related('event')

    context = {
        'user': user,
        'registrations': registrations,
    }
    return render(request, 'user_dashboard.html', context)
#-------------------------------------------------------------------------------------------------------------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Event, EventCategory, Media, EventMetric, Announcement
from .forms import EventForm, MediaForm, AnnouncementForm, EventCategoryForm
from django.utils import timezone
@login_required
def event_list(request):
    events = Event.objects.all()
    search = request.GET.get('search')
    category = request.GET.get('category')
    date_filter = request.GET.get('date')
    if search:
        events = events.filter(title__icontains=search)

    if category:
        events = events.filter(category_id=category)

    if date_filter == 'today':
        events = events.filter(event_date=timezone.now().date())
    elif date_filter == 'upcoming':
        events = events.filter(event_date__gt=timezone.now().date())
    elif date_filter == 'past':
        events = events.filter(event_date__lt=timezone.now().date())
    for event in events:
        metric = EventMetric.objects.filter(event=event).first()
        if metric:
            event.spots_left = max(event.max_participants - metric.registrations, 0)
            event.percent_filled = round((metric.registrations / event.max_participants) * 100) if event.max_participants else 0
            event.has_metric = True
        else:
            event.spots_left = event.max_participants
            event.percent_filled = 0
            event.has_metric = False
    categories = EventCategory.objects.all()
    today = timezone.now().date()

    given_feedback_event_ids = set()
    if request.user.is_authenticated:
        given_feedback_event_ids = set(
            Feedback.objects.filter(user=request.user).values_list('event_id', flat=True)
        )

    context = {
        'events': events,
        'categories': categories,
        'today': today,
        'given_feedback_event_ids': given_feedback_event_ids
    }
    return render(request, 'event_list.html', context)


@login_required
def event_detail(request, event_id):
    event = Event.objects.get(pk=event_id)
    media = event.media_set.all()
    announcements = event.announcement_set.all()
    today = timezone.now().date()

    # Check if user submitted feedback
    feedback_submitted = False
    if request.user.is_authenticated:
        feedback_submitted = Feedback.objects.filter(user=request.user, event=event).exists()

    context = {
        'event': event,
        'media': media,
        'announcements': announcements,
        'today': today,
        'feedback_submitted': feedback_submitted,
    }
    return render(request, 'event_detail.html', context)

@login_required
def create_event(request):
    if not request.user.is_superuser:
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            EventMetric.objects.create(event=event)
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.organizer and not request.user.is_superuser:
        return redirect('event_detail', event_id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event_id)
    else:
        form = EventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form, 'event': event})

@login_required
def media_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    media = Media.objects.filter(event=event)
    return render(request, 'media_list.html', {'event': event, 'media': media})

@login_required
def upload_media(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not request.user.is_superuser:
        return redirect('event_detail', event_id=event_id)

    if request.method == 'POST':
        form = MediaForm(request.POST)
        if form.is_valid():
            media = form.save(commit=False)
            media.event = event
            media.save()
            return redirect('media_list', event_id=event_id)
    else:
        form = MediaForm()
    return render(request, 'upload_media.html', {'form': form, 'event': event})

@login_required
def event_metrics(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    metrics = get_object_or_404(EventMetric, event=event)
    return render(request, 'event_metrics.html', {'event': event, 'metrics': metrics})

@login_required
def announcement_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    announcements = Announcement.objects.filter(event=event)
    return render(request, 'announcement_list.html', {'event': event, 'announcements': announcements})

@login_required
def create_announcement(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not request.user.is_superuser:
        return redirect('event_detail', event_id=event_id)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.event = event
            announcement.save()
            return redirect('announcement_list', event_id=event_id)
    else:
        form = AnnouncementForm()
    return render(request, 'create_announcement.html', {'form': form, 'event': event})

@login_required
def create_category(request):
    if not request.user.is_superuser:
        return redirect('event_list')

    if request.method == 'POST':
        form = EventCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_event')
    else:
        form = EventCategoryForm()
    return render(request, 'create_category.html', {'form': form})

#---------------------------------------------------------------------------------------------------------------------------
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Cannot register for past events
    if event.event_date < now().date():
        messages.error(request, "You cannot register for past events.")
        return redirect('event_list')

    # User must be logged in
    if not request.user.is_authenticated:
        messages.error(request, "Please login to register for an event.")
        return redirect('login')

    # Already registered
    if EventRegistration.objects.filter(user=request.user, event=event, status='registered').exists():
        messages.warning(request, "You are already registered for this event.")
        return redirect('event_list')

    # Check for event capacity
    registration_count = EventRegistration.objects.filter(event=event, status='registered').count()
    if registration_count >= event.max_participants:
        messages.error(request, "Sorry, the event is full.")
        return redirect('event_list')

    # Create registration
    EventRegistration.objects.create(
        user=request.user,
        event=event,
        status='registered'
    )

    # Update event metrics
    metric, created = EventMetric.objects.get_or_create(event=event)
    metric.registrations += 1
    metric.save()

    # ✅ Send Email Notification
    subject = f"Registration Confirmed: {event.title}"
    message = (
        f"Hello {request.user.username},\n\n"
        f"You have successfully registered for the event:\n"
        f"Title: {event.title}\n"
        f"Date: {event.event_date}\n"
        f"Time: {event.start_time} - {event.end_time}\n"
        f"Location: {event.location}\n\n"
        f"Thank you for registering!"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False
        )
    except Exception as e:
        # Optional: log error or show a message
        print("Email sending failed:", e)

    # ✅ In-App Notification (optional)
    Notification.objects.create(
        user=request.user,
        message=f"You have successfully registered for '{event.title}'."
    )

    messages.success(request, f"Successfully registered for {event.title}. A confirmation email has been sent.")
    return redirect('event_list')


def submit_feedback(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Only allow feedback after event has ended
    if event.event_date > timezone.now().date():
        messages.error(request, "You can only submit feedback after the event is completed.")
        return redirect('event_detail', event_id=event.id)

    # Check if the user participated
    if not EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.error(request, "You did not participate in this event.")
        return redirect('event_detail', event_id=event.id)

    # Check if feedback already exists
    if Feedback.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, "You have already submitted feedback for this event.")
        return redirect('event_detail', event_id=event.id)

    # Handle feedback form
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('event_detail', event_id=event.id)
    else:
        form = FeedbackForm()

    return render(request, 'submit_feedback.html', {
        'form': form,
        'event': event,
    })

@staff_member_required
def admin_dashboard(request):
    events = Event.objects.all().order_by('-event_date')
    return render(request, 'admin_panel/dashboard.html', {'events': events})

@staff_member_required
def admin_event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registrations = EventRegistration.objects.filter(event=event).select_related('user')
    return render(request, 'admin_panel/event_detail.html', {
        'event': event,
        'registrations': registrations
    })


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            full_message = f"""
            You received a new contact message:

            Name: {name}
            Email: {email}
            Subject: {subject}

            Message:
            {message}
            """

            send_mail(
                subject=f"[Contact Us] {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['balajiguduru828@gmail.com'],  # Replace with your email
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully.")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})