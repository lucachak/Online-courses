from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    def __str__(self):
        return f"Student Profile: {self.user.username}"
    
    @property
    def enrolled_courses(self):
        """Get enrolled courses through enrollments"""
        from courses.models import Course
        return Course.objects.filter(enrollments__student=self.user)
    
    @property
    def completed_lessons(self):
        """Get completed lessons through lesson progress"""
        from courses.models import Lesson
        from enrollments.models import Enrollment, LessonProgress
        enrollments = Enrollment.objects.filter(student=self.user)
        return Lesson.objects.filter(
            progress_records__enrollment__in=enrollments,
            progress_records__is_completed=True
        ).distinct()


class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    expertise = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Instructor Profile: {self.user.username}"

