from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class College(models.Model):
    name = models.CharField(max_length=150, unique=True,default="")
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class EventCategory(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.category_name

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    college = models.ForeignKey(College, on_delete=models.CASCADE)  # Linked to College
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_participants = models.IntegerField()
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Media(models.Model):
    MEDIA_TYPES = (('image', 'Image'), ('video', 'Video'), ('poster', 'Poster'))
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file_path = models.TextField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class EventMetric(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE,related_name='metrics')
    views = models.IntegerField(default=0)
    registrations = models.IntegerField(default=0)
    attendance_count = models.IntegerField(default=0)
    feedback_count = models.IntegerField(default=0)

class Announcement(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"Feedback by {self.user} for {self.event}"

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    certificate_link = models.TextField()
    issued_on = models.DateField()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class EventRegistration(models.Model):
    STATUS_CHOICES = (('registered', 'Registered'), ('cancelled', 'Cancelled'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

class Attendance(models.Model):
    STATUS_CHOICES = (('present', 'Present'), ('absent', 'Absent'))
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

class GlobalAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title