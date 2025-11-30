from rest_framework import serializers
from .models import Category, Course, Module, Lesson, Content


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    courses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'courses_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_courses_count(self, obj):
        return obj.courses.filter(status='published').count()


class ContentSerializer(serializers.ModelSerializer):
    """Serializer for Content model"""
    class Meta:
        model = Content
        fields = ['id', 'content_type', 'video_url', 'text_content', 
                  'file', 'external_link', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""
    content = ContentSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'description', 'lesson_type', 
                  'order', 'duration_minutes', 'is_free_preview', 
                  'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing lessons"""
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'order', 'duration_minutes', 
                  'is_free_preview']


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module model"""
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'order', 
                  'lessons', 'lessons_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()


class ModuleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing modules"""
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'lessons_count']
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    instructor = serializers.StringRelatedField(read_only=True)
    instructor_id = serializers.IntegerField(write_only=True, required=False)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    modules = ModuleSerializer(many=True, read_only=True)
    modules_count = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    enrollments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'short_description', 'description', 'instructor', 
                  'instructor_id', 'category', 'category_id', 'thumbnail', 'background_image', 
                  'price', 'level', 'duration_hours', 'status', 'featured', 'modules', 
                  'modules_count', 'total_lessons', 'enrollments_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_modules_count(self, obj):
        return obj.modules.count()
    
    def get_total_lessons(self, obj):
        return Lesson.objects.filter(module__course=obj).count()
    
    def get_enrollments_count(self, obj):
        return obj.enrollments.count()
    
    def create(self, validated_data):
        instructor_id = validated_data.pop('instructor_id', None)
        category_id = validated_data.pop('category_id', None)
        
        if instructor_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            validated_data['instructor'] = User.objects.get(id=instructor_id)
        elif 'instructor' not in validated_data and self.context.get('request'):
            validated_data['instructor'] = self.context['request'].user
        
        if category_id:
            validated_data['category'] = Category.objects.get(id=category_id)
        
        return super().create(validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing courses"""
    instructor = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    modules_count = serializers.SerializerMethodField()
    enrollments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'short_description', 'description', 'instructor', 
                  'category', 'thumbnail', 'background_image', 'price', 'level', 
                  'duration_hours', 'status', 'featured', 'modules_count', 
                  'enrollments_count', 'created_at']
    
    def get_modules_count(self, obj):
        return obj.modules.count()
    
    def get_enrollments_count(self, obj):
        return obj.enrollments.count()

