from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from django.utils.html import format_html
from .models import Enrollment, LessonProgress, CourseProgress


class LessonProgressInline(TabularInline):
    """Inline admin for LessonProgress model"""
    model = LessonProgress
    extra = 0
    fields = ['lesson', 'is_completed', 'watched_duration', 'last_watched_at', 'completed_at']
    readonly_fields = ['last_watched_at', 'completed_at']
    sortable_by = ['lesson__order']


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    """Admin interface for Enrollment model"""
    list_display = ['student', 'course', 'status_display', 'progress_percentage_display', 'enrolled_at', 'completed_at']
    list_filter = ['status', 'enrolled_at', 'completed_at']
    search_fields = ['student__username', 'student__email', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at', 'progress_percentage']
    inlines = [LessonProgressInline]
    list_per_page = 25
    list_select_related = ['student', 'course']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'course', 'status'),
            'classes': ('wide',)
        }),
        ('Progress', {
            'fields': ('progress_percentage',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Status', ordering='status')
    def status_display(self, obj):
        colors = {
            'active': '#10b981',
            'completed': '#3b82f6',
            'dropped': '#ef4444'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_status_display()
        )
    
    @display(description='Progress', ordering='progress_percentage')
    def progress_percentage_display(self, obj):
        percentage = float(obj.progress_percentage)
        if percentage >= 100:
            color = '#10b981'
            icon = '✅'
        elif percentage >= 50:
            color = '#3b82f6'
            icon = '🔄'
        elif percentage > 0:
            color = '#f59e0b'
            icon = '⏳'
        else:
            color = '#6b7280'
            icon = '⭕'
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;"><span>{}</span><span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{:.1f}%</span></div>',
            icon,
            color,
            percentage
        )
    
    actions = ['mark_as_completed', 'mark_as_active', 'mark_as_dropped']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected enrollments as completed"""
        from django.utils import timezone
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{updated} enrollment(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected enrollments as completed'
    
    def mark_as_active(self, request, queryset):
        """Mark selected enrollments as active"""
        updated = queryset.update(status='active', completed_at=None)
        self.message_user(request, f'{updated} enrollment(s) marked as active.')
    mark_as_active.short_description = 'Mark selected enrollments as active'
    
    def mark_as_dropped(self, request, queryset):
        """Mark selected enrollments as dropped"""
        updated = queryset.update(status='dropped')
        self.message_user(request, f'{updated} enrollment(s) marked as dropped.')
    mark_as_dropped.short_description = 'Mark selected enrollments as dropped'


@admin.register(LessonProgress)
class LessonProgressAdmin(ModelAdmin):
    """Admin interface for LessonProgress model"""
    list_display = ['enrollment', 'lesson', 'is_completed_display', 'watched_duration_display', 'last_watched_at', 'completed_at']
    list_filter = ['is_completed', 'last_watched_at', 'completed_at', 'enrollment__course']
    search_fields = ['enrollment__student__username', 'enrollment__student__email', 'lesson__title', 'lesson__module__course__title']
    readonly_fields = ['last_watched_at', 'completed_at']
    list_per_page = 25
    list_select_related = ['enrollment', 'enrollment__student', 'enrollment__course', 'lesson', 'lesson__module']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('enrollment', 'lesson'),
            'classes': ('wide',)
        }),
        ('Progress', {
            'fields': ('is_completed', 'watched_duration'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('last_watched_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Completed', boolean=True)
    def is_completed_display(self, obj):
        return obj.is_completed
    
    @display(description='Duration Watched', ordering='watched_duration')
    def watched_duration_display(self, obj):
        hours = obj.watched_duration // 3600
        minutes = (obj.watched_duration % 3600) // 60
        seconds = obj.watched_duration % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    
    actions = ['mark_as_completed', 'mark_as_incomplete']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected lessons as completed"""
        from django.utils import timezone
        updated = queryset.update(is_completed=True, completed_at=timezone.now())
        self.message_user(request, f'{updated} lesson(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected lessons as completed'
    
    def mark_as_incomplete(self, request, queryset):
        """Mark selected lessons as incomplete"""
        updated = queryset.update(is_completed=False, completed_at=None)
        self.message_user(request, f'{updated} lesson(s) marked as incomplete.')
    mark_as_incomplete.short_description = 'Mark selected lessons as incomplete'


@admin.register(CourseProgress)
class CourseProgressAdmin(ModelAdmin):
    """Admin interface for CourseProgress model"""
    list_display = ['enrollment', 'progress_summary', 'last_accessed_at', 'updated_at']
    list_filter = ['updated_at', 'last_accessed_at']
    search_fields = ['enrollment__student__username', 'enrollment__student__email', 'enrollment__course__title']
    readonly_fields = ['enrollment', 'total_lessons', 'completed_lessons', 'progress_percentage', 'last_accessed_at', 'updated_at']
    list_per_page = 25
    list_select_related = ['enrollment', 'enrollment__student', 'enrollment__course']
    
    fieldsets = (
        ('Enrollment', {
            'fields': ('enrollment',),
            'classes': ('wide',)
        }),
        ('Progress Statistics', {
            'fields': ('total_lessons', 'completed_lessons', 'progress_percentage'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('last_accessed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Progress Summary')
    def progress_summary(self, obj):
        percentage = float(obj.progress_percentage)
        completed = obj.completed_lessons
        total = obj.total_lessons
        
        if percentage >= 100:
            color = '#10b981'
            icon = '✅'
        elif percentage >= 50:
            color = '#3b82f6'
            icon = '🔄'
        elif percentage > 0:
            color = '#f59e0b'
            icon = '⏳'
        else:
            color = '#6b7280'
            icon = '⭕'
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<span>{}</span>'
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{:.1f}%</span>'
            '<span style="color: #6b7280; font-size: 12px;">({}/{})</span>'
            '</div>',
            icon,
            color,
            percentage,
            completed,
            total
        )
    
    actions = ['recalculate_progress']
    
    def recalculate_progress(self, request, queryset):
        """Recalculate progress for selected items"""
        for progress in queryset:
            progress.update_progress()
        self.message_user(request, f'{queryset.count()} progress record(s) recalculated.')
    recalculate_progress.short_description = 'Recalculate progress for selected items'

