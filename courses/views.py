from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q
from .models import Category, Course, Module, Lesson, Content
from .serializers import (
    CategorySerializer,
    CourseSerializer, CourseListSerializer,
    ModuleSerializer, ModuleListSerializer,
    LessonSerializer, LessonListSerializer,
    ContentSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses
    """
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    
    def get_queryset(self):
        queryset = Course.objects.all()
        status_filter = self.request.query_params.get('status', None)
        level_filter = self.request.query_params.get('level', None)
        instructor_filter = self.request.query_params.get('instructor', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if level_filter:
            queryset = queryset.filter(level=level_filter)
        if instructor_filter:
            queryset = queryset.filter(instructor_id=instructor_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the instructor to the current user if not specified"""
        if 'instructor' not in serializer.validated_data:
            serializer.save(instructor=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def modules(self, request, pk=None):
        """Get all modules for a course"""
        course = self.get_object()
        modules = course.modules.all()
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def lessons(self, request, pk=None):
        """Get all lessons for a course"""
        course = self.get_object()
        lessons = Lesson.objects.filter(module__course=course)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """Enroll current user in a course"""
        course = self.get_object()
        from enrollments.models import Enrollment
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        if created:
            return Response(
                {'detail': 'Successfully enrolled in course'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'detail': 'Already enrolled in this course'},
            status=status.HTTP_200_OK
        )


class ModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing modules
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ModuleListSerializer
        return ModuleSerializer
    
    def get_queryset(self):
        queryset = Module.objects.all()
        course_id = self.request.query_params.get('course', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def lessons(self, request, pk=None):
        """Get all lessons for a module"""
        module = self.get_object()
        lessons = module.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lessons
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        return LessonSerializer
    
    def get_queryset(self):
        queryset = Lesson.objects.all()
        module_id = self.request.query_params.get('module', None)
        course_id = self.request.query_params.get('course', None)
        
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        if course_id:
            queryset = queryset.filter(module__course_id=course_id)
        
        return queryset
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def content(self, request, pk=None):
        """Get content for a lesson"""
        lesson = self.get_object()
        try:
            content = lesson.content
            serializer = ContentSerializer(content)
            return Response(serializer.data)
        except Content.DoesNotExist:
            return Response(
                {'detail': 'No content available for this lesson'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_complete(self, request, pk=None):
        """Mark a lesson as completed for the current user"""
        lesson = self.get_object()
        from enrollments.models import Enrollment, LessonProgress
        
        # Find user's enrollment for this course
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=lesson.module.course
        ).first()
        
        if not enrollment:
            return Response(
                {'detail': 'You must be enrolled in this course to mark lessons as complete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        progress.is_completed = True
        progress.save()
        
        return Response({'detail': 'Lesson marked as complete'})


class ContentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lesson content
    """
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

