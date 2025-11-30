from rest_framework import serializers
from .models import Enrollment, LessonProgress, CourseProgress
from courses.serializers import CourseListSerializer, LessonListSerializer


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for LessonProgress model"""
    lesson = LessonListSerializer(read_only=True)
    lesson_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LessonProgress
        fields = ['id', 'enrollment', 'lesson', 'lesson_id', 'is_completed', 
                  'watched_duration', 'last_watched_at', 'completed_at']
        read_only_fields = ['id', 'last_watched_at', 'completed_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""
    student = serializers.StringRelatedField(read_only=True)
    course = CourseListSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    lesson_progress = LessonProgressSerializer(many=True, read_only=True)
    completed_lessons_count = serializers.SerializerMethodField()
    total_lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_id', 'status', 
                  'enrolled_at', 'completed_at', 'progress_percentage', 
                  'lesson_progress', 'completed_lessons_count', 
                  'total_lessons_count']
        read_only_fields = ['id', 'student', 'enrolled_at', 'completed_at', 
                           'progress_percentage']
    
    def get_completed_lessons_count(self, obj):
        return obj.lesson_progress.filter(is_completed=True).count()
    
    def get_total_lessons_count(self, obj):
        from courses.models import Lesson
        return Lesson.objects.filter(module__course=obj.course).count()
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing enrollments"""
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'status', 'progress_percentage', 
                  'enrolled_at', 'completed_at']


class CourseProgressSerializer(serializers.ModelSerializer):
    """Serializer for CourseProgress model"""
    enrollment = EnrollmentListSerializer(read_only=True)
    
    class Meta:
        model = CourseProgress
        fields = ['id', 'enrollment', 'total_lessons', 'completed_lessons', 
                  'progress_percentage', 'last_accessed_at', 'updated_at']
        read_only_fields = ['id', 'total_lessons', 'completed_lessons', 
                           'progress_percentage', 'last_accessed_at', 'updated_at']

