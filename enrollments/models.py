from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'user_type': 'student'}
    )
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    def update_progress(self):
        """Calculate and update progress percentage based on completed lessons"""
        total_lessons = self.course.modules.aggregate(
            total=models.Count('lessons')
        )['total'] or 0
        
        if total_lessons == 0:
            self.progress_percentage = 0.00
        else:
            completed_count = self.lesson_progress.filter(is_completed=True).count()
            self.progress_percentage = (completed_count / total_lessons) * 100
        
        self.save()


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, related_name='progress_records')
    is_completed = models.BooleanField(default=False)
    watched_duration = models.PositiveIntegerField(default=0)  # in seconds
    last_watched_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']
        ordering = ['lesson__order']
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.lesson.title}"
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
        # Update enrollment progress when lesson progress changes
        self.enrollment.update_progress()


class CourseProgress(models.Model):
    """Overall course progress tracking for a student"""
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='course_progress'
    )
    total_lessons = models.PositiveIntegerField(default=0)
    completed_lessons = models.PositiveIntegerField(default=0)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_accessed_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Course Progress'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.enrollment.course.title} - {self.progress_percentage}%"
    
    def update_progress(self, save=True):
        """Recalculate progress from enrollment"""
        enrollment = self.enrollment
        self.total_lessons = LessonProgress.objects.filter(
            enrollment=enrollment
        ).values('lesson').distinct().count()
        
        self.completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).values('lesson').distinct().count()
        
        if self.total_lessons > 0:
            self.progress_percentage = (self.completed_lessons / self.total_lessons) * 100
        else:
            self.progress_percentage = 0.00
        
        if save:
            # Use update() to avoid triggering save() again
            CourseProgress.objects.filter(pk=self.pk).update(
                total_lessons=self.total_lessons,
                completed_lessons=self.completed_lessons,
                progress_percentage=self.progress_percentage
            )
    
    def save(self, *args, **kwargs):
        """Auto-update progress on save for new instances"""
        if not self.pk:  # New instance - calculate progress first
            # Calculate progress values
            enrollment = self.enrollment
            self.total_lessons = LessonProgress.objects.filter(
                enrollment=enrollment
            ).values('lesson').distinct().count()
            
            self.completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).values('lesson').distinct().count()
            
            if self.total_lessons > 0:
                self.progress_percentage = (self.completed_lessons / self.total_lessons) * 100
            else:
                self.progress_percentage = 0.00
        
        super().save(*args, **kwargs)

