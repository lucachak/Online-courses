from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, StudentProfile, InstructorProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'profile_picture', 'bio', 'date_joined', 
                  'updated_at', 'password', 'password2']
        read_only_fields = ['id', 'date_joined', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (without password)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'profile_picture', 'bio', 'date_joined', 
                  'updated_at']
        read_only_fields = ['id', 'username', 'date_joined', 'updated_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    user = UserSerializer(read_only=True)
    enrolled_courses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'enrolled_courses_count']
        read_only_fields = ['id']
    
    def get_enrolled_courses_count(self, obj):
        return obj.enrolled_courses.count()


class InstructorProfileSerializer(serializers.ModelSerializer):
    """Serializer for InstructorProfile model"""
    user = UserSerializer(read_only=True)
    courses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InstructorProfile
        fields = ['id', 'user', 'expertise', 'website', 'social_links', 'courses_count']
        read_only_fields = ['id']
    
    def get_courses_count(self, obj):
        return obj.user.courses.count()

