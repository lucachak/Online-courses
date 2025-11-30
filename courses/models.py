from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    """Course categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon class or name
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        limit_choices_to={'user_type': 'instructor'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    background_image = models.ImageField(upload_to='course_backgrounds/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_hours = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exclude(pk=self.pk if self.pk else None).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    LESSON_TYPES = (
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='video')
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_free_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.course.title} - {self.title}"


class Content(models.Model):
    CONTENT_TYPES = (
        ('video', 'Video'),
        ('text', 'Text'),
        ('file', 'File'),
        ('link', 'Link'),
    )
    
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='content')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='video')
    video_url = models.URLField(blank=True, null=True)
    text_content = models.TextField(blank=True)
    file = models.FileField(upload_to='lesson_files/', blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Content for {self.lesson.title}"

