from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display
from django.utils.html import format_html
from .models import Category, Course, Module, Lesson, Content


class ContentInline(StackedInline):
    """Inline admin for Content model"""
    model = Content
    extra = 0
    fields = ['content_type', 'video_url', 'text_content', 'file', 'external_link']
    classes = ['collapse']


class LessonInline(TabularInline):
    """Inline admin for Lesson model"""
    model = Lesson
    extra = 0
    fields = ['title', 'lesson_type', 'order', 'duration_minutes', 'is_free_preview']
    show_change_link = True
    sortable_by = ['order']


class ModuleInline(StackedInline):
    """Inline admin for Module model"""
    model = Module
    extra = 0
    fields = ['title', 'description', 'order']
    show_change_link = True
    classes = ['collapse']
    sortable_by = ['order']


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin interface for Category model"""
    list_display = ['name', 'slug', 'get_courses_count_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Courses', ordering='courses__count')
    def get_courses_count_display(self, obj):
        count = obj.courses.filter(status='published').count()
        if count > 0:
            return format_html(
                '<span style="background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
                count
            )
        return format_html('<span style="color: #6b7280;">0</span>')


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    """Admin interface for Course model"""
    list_display = ['thumbnail_display', 'title', 'instructor', 'category', 'level_display', 'price_display', 'status_display', 'featured_display', 'get_enrollments_count_display', 'created_at']
    list_filter = ['status', 'level', 'featured', 'category', 'created_at']
    search_fields = ['title', 'description', 'short_description', 'instructor__username', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'get_enrollments_count_display']
    inlines = [ModuleInline]
    list_per_page = 25
    list_select_related = ['instructor', 'category']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'instructor', 'category'),
            'classes': ('wide',)
        }),
        ('Media', {
            'fields': ('thumbnail', 'background_image'),
            'classes': ('wide',)
        }),
        ('Course Details', {
            'fields': ('price', 'level', 'duration_hours', 'status', 'featured'),
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': ('get_enrollments_count_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Thumbnail')
    def thumbnail_display(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail.url
            )
        return format_html('<span style="color: #9ca3af;">No image</span>')
    
    @display(description='Level', ordering='level')
    def level_display(self, obj):
        colors = {
            'beginner': '#10b981',
            'intermediate': '#f59e0b',
            'advanced': '#ef4444'
        }
        color = colors.get(obj.level, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_level_display()
        )
    
    @display(description='Price', ordering='price')
    def price_display(self, obj):
        return format_html('<strong style="color: #3b82f6;">${}</strong>', obj.price)
    
    @display(description='Status', ordering='status')
    def status_display(self, obj):
        colors = {
            'draft': '#6b7280',
            'published': '#10b981',
            'archived': '#ef4444'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_status_display()
        )
    
    @display(description='Featured', boolean=True)
    def featured_display(self, obj):
        return obj.featured
    
    @display(description='Enrollments', ordering='enrollments__count')
    def get_enrollments_count_display(self, obj):
        count = obj.enrollments.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #8b5cf6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
                count
            )
        return format_html('<span style="color: #6b7280;">0</span>')


@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    """Admin interface for Module model"""
    list_display = ['title', 'course', 'order', 'get_lessons_count_display', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [LessonInline]
    list_per_page = 25
    list_select_related = ['course']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'order'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Lessons', ordering='lessons__count')
    def get_lessons_count_display(self, obj):
        count = obj.lessons.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #06b6d4; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
                count
            )
        return format_html('<span style="color: #6b7280;">0</span>')


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    """Admin interface for Lesson model"""
    list_display = ['title', 'module', 'lesson_type_display', 'order', 'duration_display', 'is_free_preview_display']
    list_filter = ['lesson_type', 'is_free_preview', 'module__course']
    search_fields = ['title', 'description', 'module__title', 'module__course__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ContentInline]
    list_per_page = 25
    list_select_related = ['module', 'module__course']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'description', 'lesson_type'),
            'classes': ('wide',)
        }),
        ('Details', {
            'fields': ('order', 'duration_minutes', 'is_free_preview'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Type', ordering='lesson_type')
    def lesson_type_display(self, obj):
        colors = {
            'video': '#ef4444',
            'text': '#3b82f6',
            'quiz': '#f59e0b',
            'assignment': '#8b5cf6'
        }
        color = colors.get(obj.lesson_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_lesson_type_display()
        )
    
    @display(description='Duration', ordering='duration_minutes')
    def duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    @display(description='Free Preview', boolean=True)
    def is_free_preview_display(self, obj):
        return obj.is_free_preview


@admin.register(Content)
class ContentAdmin(ModelAdmin):
    """Admin interface for Content model"""
    list_display = ['lesson', 'content_type_display', 'preview_content', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['lesson__title', 'text_content', 'video_url']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    list_select_related = ['lesson', 'lesson__module', 'lesson__module__course']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'content_type'),
            'classes': ('wide',)
        }),
        ('Content', {
            'fields': ('video_url', 'text_content', 'file', 'external_link'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Type', ordering='content_type')
    def content_type_display(self, obj):
        colors = {
            'video': '#ef4444',
            'text': '#3b82f6',
            'file': '#10b981',
            'link': '#8b5cf6'
        }
        color = colors.get(obj.content_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_content_type_display()
        )
    
    @display(description='Preview')
    def preview_content(self, obj):
        if obj.content_type == 'video' and obj.video_url:
            return format_html('<a href="{}" target="_blank" style="color: #3b82f6;">🔗 Video Link</a>', obj.video_url)
        elif obj.content_type == 'text' and obj.text_content:
            preview = obj.text_content[:50] + '...' if len(obj.text_content) > 50 else obj.text_content
            return format_html('<span style="color: #6b7280;">{}</span>', preview)
        elif obj.content_type == 'link' and obj.external_link:
            return format_html('<a href="{}" target="_blank" style="color: #3b82f6;">🔗 External Link</a>', obj.external_link)
        return format_html('<span style="color: #9ca3af;">No content</span>')

