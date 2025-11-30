from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from .models import Course, Category
from enrollments.models import Enrollment, CourseProgress


def home(request):
    """Home page with trending courses"""
    # Get trending courses (most enrollments)
    trending_courses = Course.objects.filter(
        status='published'
    ).annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count', '-created_at')[:8]
    
    # Get featured courses
    featured_courses = Course.objects.filter(
        status='published',
        featured=True
    ).order_by('-created_at')[:6]
    
    # Get recent courses
    recent_courses = Course.objects.filter(status='published').order_by('-created_at')[:12]
    
    categories = Category.objects.annotate(
        course_count=Count('courses', filter=Q(courses__status='published'))
    ).filter(course_count__gt=0)[:8]
    
    selected_course = featured_courses.first() if featured_courses.exists() else trending_courses.first()
    
    context = {
        'trending_courses': trending_courses,
        'featured_courses': featured_courses,
        'recent_courses': recent_courses,
        'categories': categories,
        'selected_course': selected_course,
    }
    return render(request, 'courses/home.html', context)


def course_list(request):
    """Course listing page"""
    category_slug = request.GET.get('category')
    level = request.GET.get('level')
    search = request.GET.get('search')
    
    courses = Course.objects.filter(status='published')
    
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if level:
        courses = courses.filter(level=level)
    if search:
        courses = courses.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    courses = courses.order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': category_slug,
        'selected_level': level,
        'search_query': search,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    """Course detail page"""
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # Handle enrollment
    if request.method == 'POST' and 'enroll' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to enroll in courses.')
            return redirect('account_login')
        
        if request.user.user_type != 'student':
            messages.error(request, 'Only students can enroll in courses.')
            return redirect('course_detail', slug=slug)
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        if created:
            CourseProgress.objects.create(enrollment=enrollment)
            messages.success(request, f'Successfully enrolled in {course.title}!')
        else:
            messages.info(request, 'You are already enrolled in this course.')
        
        return redirect('course_detail', slug=slug)
    
    # Get related courses
    related_courses = Course.objects.filter(
        status='published',
        category=course.category
    ).exclude(id=course.id)[:4]
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        try:
            enrollment = request.user.enrollments.get(course=course)
            is_enrolled = True
        except:
            pass
    
    context = {
        'course': course,
        'related_courses': related_courses,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'modules': course.modules.all().prefetch_related('lessons'),
    }
    return render(request, 'courses/course_detail.html', context)


def search_courses(request):
    """HTMX search endpoint"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return HttpResponse('')
    
    courses = Course.objects.filter(
        status='published'
    ).filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(short_description__icontains=query) |
        Q(category__name__icontains=query)
    ).select_related('category', 'instructor').annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count', '-created_at')[:8]
    
    if not courses.exists():
        return HttpResponse(
            '<div class="p-4 text-center text-gray-500 dark:text-gray-400">'
            'No courses found matching your search.'
            '</div>'
        )
    
    html = '<div class="p-2">'
    for course in courses:
        course_url = reverse('course_detail', kwargs={'slug': course.slug})
        short_desc = course.short_description or (course.description[:50] + "..." if course.description else "")
        html += f'''
        <a href="{course_url}" 
           class="flex items-center space-x-3 p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition group">
            <div class="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span class="text-white text-xl font-bold">{course.title[0] if course.title else 'C'}</span>
            </div>
            <div class="flex-1 min-w-0">
                <h4 class="text-sm font-semibold text-gray-900 dark:text-white truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                    {course.title}
                </h4>
                <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {short_desc}
                </p>
                <div class="flex items-center space-x-2 mt-1">
                    <span class="text-xs text-indigo-600 dark:text-indigo-400 font-medium">${course.price}</span>
                    <span class="text-xs text-gray-400">•</span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">{course.level.title()}</span>
                </div>
            </div>
        </a>
        '''
    html += '</div>'
    return HttpResponse(html)

