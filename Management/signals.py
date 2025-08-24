from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, EventRegistration, GlobalAnnouncement

@receiver(post_save, sender=Event)
def create_event_announcement(sender, instance, created, **kwargs):
    if created:
        GlobalAnnouncement.objects.create(
            title=f"New Event: {instance.title}",
            message=f"'{instance.title}' has been added. Don't miss it!"
        )

@receiver(post_save, sender=EventRegistration)
def register_event_announcement(sender, instance, created, **kwargs):
    if created:
        GlobalAnnouncement.objects.create(
            title=f"New Registration",
            message=f"{instance.user.first_name or instance.user.username} registered for '{instance.event.title}'."
        )
