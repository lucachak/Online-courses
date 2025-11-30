from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.utils.html import format_html
from .models import User, StudentProfile, InstructorProfile


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ['profile_picture_display', 'username', 'email', 'full_name', 'user_type_display', 'is_staff_display', 'is_active_display', 'date_joined']
    list_filter = ['user_type', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_per_page = 25
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'profile_picture', 'bio'),
            'classes': ('wide',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'profile_picture', 'bio'),
            'classes': ('wide',)
        }),
    )
    
    @display(description='Avatar')
    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%; border: 2px solid #e5e7eb;" />',
                obj.profile_picture.url
            )
        return format_html(
            '<div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px;">{}</div>',
            obj.username[0].upper() if obj.username else 'U'
        )
    
    @display(description='Full Name', ordering='first_name')
    def full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return format_html('<span style="color: #9ca3af;">—</span>')
    
    @display(description='User Type', ordering='user_type')
    def user_type_display(self, obj):
        colors = {
            'student': '#3b82f6',
            'instructor': '#8b5cf6',
            'admin': '#ef4444'
        }
        color = colors.get(obj.user_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    
    @display(description='Staff', boolean=True)
    def is_staff_display(self, obj):
        return obj.is_staff
    
    @display(description='Active', boolean=True)
    def is_active_display(self, obj):
        return obj.is_active


@admin.register(StudentProfile)
class StudentProfileAdmin(ModelAdmin):
    """Admin interface for StudentProfile model"""
    list_display = ['user', 'get_enrolled_courses_count_display', 'get_completed_lessons_count_display']
    list_filter = ['user__user_type']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['get_enrolled_courses_display', 'get_completed_lessons_display']
    list_per_page = 25
    list_select_related = ['user']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('user',),
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': ('get_enrolled_courses_count_display', 'get_completed_lessons_count_display'),
            'classes': ('wide',)
        }),
        ('Details', {
            'fields': ('get_enrolled_courses_display', 'get_completed_lessons_display'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Enrolled Courses', ordering='enrolled_courses__count')
    def get_enrolled_courses_count_display(self, obj):
        count = obj.enrolled_courses.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{} courses</span>',
                count
            )
        return format_html('<span style="color: #6b7280;">No enrollments</span>')
    
    @display(description='Completed Lessons', ordering='completed_lessons__count')
    def get_completed_lessons_count_display(self, obj):
        count = obj.completed_lessons.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{} lessons</span>',
                count
            )
        return format_html('<span style="color: #6b7280;">0 lessons</span>')
    
    @display(description='Enrolled Courses List')
    def get_enrolled_courses_display(self, obj):
        courses = obj.enrolled_courses[:10]
        if courses:
            html = '<ul style="list-style: none; padding: 0;">'
            for course in courses:
                html += f'<li style="padding: 4px 0; border-bottom: 1px solid #e5e7eb;">📚 {course.title}</li>'
            html += '</ul>'
            return format_html(html)
        return format_html('<span style="color: #9ca3af;">No enrolled courses</span>')
    
    @display(description='Completed Lessons List')
    def get_completed_lessons_display(self, obj):
        lessons = obj.completed_lessons[:10]
        if lessons:
            html = '<ul style="list-style: none; padding: 0;">'
            for lesson in lessons:
                html += f'<li style="padding: 4px 0; border-bottom: 1px solid #e5e7eb;">✅ {lesson.title}</li>'
            html += '</ul>'
            return format_html(html)
        return format_html('<span style="color: #9ca3af;">No completed lessons</span>')


@admin.register(InstructorProfile)
class InstructorProfileAdmin(ModelAdmin):
    """Admin interface for InstructorProfile model"""
    list_display = ['user', 'expertise', 'website_display', 'get_courses_count_display']
    list_filter = ['expertise']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'expertise']
    list_per_page = 25
    list_select_related = ['user']
    
    fieldsets = (
        ('Instructor Information', {
            'fields': ('user', 'expertise', 'website'),
            'classes': ('wide',)
        }),
        ('Social Links', {
            'fields': ('social_links',),
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': ('get_courses_count_display',),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Website')
    def website_display(self, obj):
        if obj.website:
            return format_html(
                '<a href="{}" target="_blank" style="color: #3b82f6; text-decoration: none;">🔗 {}</a>',
                obj.website,
                obj.website
            )
        return format_html('<span style="color: #9ca3af;">—</span>')
    
    @display(description='Courses', ordering='user__courses__count')
    def get_courses_count_display(self, obj):
        count = obj.user.courses.filter(status='published').count()
        if count > 0:
            return format_html(
                '<span style="background-color: #8b5cf6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{} courses</span>',
                count
            )
        return format_html('<span style="color: #6b7280;">0 courses</span>')

