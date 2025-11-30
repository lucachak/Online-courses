from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import User, StudentProfile, InstructorProfile
from enrollments.models import Enrollment


@login_required
def user_settings(request):
    """User settings page"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.bio = request.POST.get('bio', '')
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_settings')
    
    context = {
        'user': request.user,
    }
    return render(request, 'users/user_settings.html', context)


@login_required
def professor_settings(request, *args, **kwargs):
    """Professor/Instructor settings page"""
    if request.user.user_type != 'instructor':
        messages.error(request, 'Only instructors can access this page.')
        return redirect('home')
    
    instructor_profile, created = InstructorProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.bio = request.POST.get('bio', '')
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        instructor_profile.expertise = request.POST.get('expertise', '')
        instructor_profile.website = request.POST.get('website', '')
        
        user.save()
        instructor_profile.save()
        messages.success(request, 'Instructor profile updated successfully!')
        return redirect('professor_settings')
    
    # Get instructor's courses
    instructor_courses = user.courses.filter(status='published').order_by('-created_at')[:10]
    
    context = {
        'user': request.user,
        'instructor_profile': instructor_profile,
        'courses': instructor_courses,
    }
    return render(request, 'users/professor_settings.html', context)


@login_required
def admin_settings(request):
    """Admin settings page"""
    if not request.user.is_staff and request.user.user_type != 'admin':
        messages.error(request, 'Only administrators can access this page.')
        return redirect('home')
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.bio = request.POST.get('bio', '')
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Admin profile updated successfully!')
        return redirect('admin_settings')
    
    # Get admin statistics
    from courses.models import Course, Category
    from django.db.models import Count
    
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(status='published').count()
    total_students = User.objects.filter(user_type='student').count()
    total_instructors = User.objects.filter(user_type='instructor').count()
    total_enrollments = Enrollment.objects.count()
    
    context = {
        'user': request.user,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_enrollments': total_enrollments,
    }
    return render(request, 'users/admin_settings.html', context)

