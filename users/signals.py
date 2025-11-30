from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile, InstructorProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created"""
    if created:
        if instance.user_type == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.user_type == 'instructor':
            InstructorProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, **kwargs):
    """Update profile when user type changes"""
    if instance.user_type == 'student':
        StudentProfile.objects.get_or_create(user=instance)
        # Remove instructor profile if exists
        InstructorProfile.objects.filter(user=instance).delete()
    elif instance.user_type == 'instructor':
        InstructorProfile.objects.get_or_create(user=instance)
        # Remove student profile if exists
        StudentProfile.objects.filter(user=instance).delete()

