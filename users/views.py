from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .models import StudentProfile, InstructorProfile
from .serializers import (
    UserSerializer, UserUpdateSerializer, 
    StudentProfileSerializer, InstructorProfileSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]  # Allow registration
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserSerializer
        return UserUpdateSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [AllowAny]  # Allow anyone to register
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing student profiles
    """
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """Get current user's student profile"""
        try:
            profile = request.user.student_profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response(
                {'detail': 'Student profile does not exist. Please create one.'},
                status=status.HTTP_404_NOT_FOUND
            )


class InstructorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing instructor profiles
    """
    queryset = InstructorProfile.objects.all()
    serializer_class = InstructorProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        """Get current user's instructor profile"""
        try:
            profile = request.user.instructor_profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except InstructorProfile.DoesNotExist:
            return Response(
                {'detail': 'Instructor profile does not exist. Please create one.'},
                status=status.HTTP_404_NOT_FOUND
            )

