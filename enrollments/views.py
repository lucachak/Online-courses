from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Enrollment, LessonProgress
from .serializers import EnrollmentSerializer, EnrollmentListSerializer, LessonProgressSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EnrollmentListSerializer
        return EnrollmentSerializer
    
    def get_queryset(self):
        """Return enrollments for the current user"""
        user = self.request.user
        queryset = Enrollment.objects.filter(student=user)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the student to the current user"""
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def progress(self, request, pk=None):
        """Get detailed progress for an enrollment"""
        enrollment = self.get_object()
        
        # Verify ownership
        if enrollment.student != request.user:
            return Response(
                {'detail': 'You do not have permission to view this enrollment'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Mark an enrollment as completed"""
        enrollment = self.get_object()
        
        # Verify ownership
        if enrollment.student != request.user:
            return Response(
                {'detail': 'You do not have permission to modify this enrollment'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollment.status = 'completed'
        from django.utils import timezone
        enrollment.completed_at = timezone.now()
        enrollment.save()
        
        return Response({'detail': 'Enrollment marked as completed'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_enrollments(self, request):
        """Get all enrollments for the current user"""
        enrollments = self.get_queryset()
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)


class LessonProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lesson progress
    """
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return lesson progress for the current user's enrollments"""
        user = self.request.user
        enrollments = Enrollment.objects.filter(student=user)
        return LessonProgress.objects.filter(enrollment__in=enrollments)
    
    def perform_create(self, serializer):
        """Set the enrollment based on lesson"""
        lesson = serializer.validated_data['lesson']
        enrollment = Enrollment.objects.filter(
            student=self.request.user,
            course=lesson.module.course
        ).first()
        
        if not enrollment:
            raise serializers.ValidationError(
                'You must be enrolled in this course to track progress'
            )
        
        serializer.save(enrollment=enrollment)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_watch_time(self, request, pk=None):
        """Update watch time for a lesson"""
        progress = self.get_object()
        
        # Verify ownership
        if progress.enrollment.student != request.user:
            return Response(
                {'detail': 'You do not have permission to update this progress'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        watched_duration = request.data.get('watched_duration', 0)
        progress.watched_duration = max(progress.watched_duration, int(watched_duration))
        progress.save()
        
        return Response({
            'detail': 'Watch time updated',
            'watched_duration': progress.watched_duration
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_complete(self, request, pk=None):
        """Mark a lesson as completed"""
        progress = self.get_object()
        
        # Verify ownership
        if progress.enrollment.student != request.user:
            return Response(
                {'detail': 'You do not have permission to update this progress'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        progress.is_completed = True
        progress.save()
        
        return Response({'detail': 'Lesson marked as complete'})

