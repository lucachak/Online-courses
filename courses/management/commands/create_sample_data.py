from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Module, Lesson, Content
from enrollments.models import Enrollment, LessonProgress, CourseProgress

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the course platform'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories = []
        category_data = [
            {'name': 'Web Development', 'description': 'Learn modern web development', 'icon': 'code'},
            {'name': 'Data Science', 'description': 'Master data science and analytics', 'icon': 'chart'},
            {'name': 'Mobile Development', 'description': 'Build mobile applications', 'icon': 'mobile'},
            {'name': 'Design', 'description': 'UI/UX and graphic design', 'icon': 'palette'},
            {'name': 'Programming', 'description': 'Learn programming languages', 'icon': 'code'},
            {'name': 'Business', 'description': 'Business and entrepreneurship', 'icon': 'briefcase'},
            {'name': 'Marketing', 'description': 'Digital marketing and SEO', 'icon': 'megaphone'},
            {'name': 'Photography', 'description': 'Photography and videography', 'icon': 'camera'},
        ]
        
        for cat_data in category_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
        
        # Create instructor
        instructor, created = User.objects.get_or_create(
            email='instructor@example.com',
            defaults={
                'username': 'instructor',
                'user_type': 'instructor',
                'first_name': 'John',
                'last_name': 'Doe',
            }
        )
        if created:
            instructor.set_password('password123')
            instructor.save()
            self.stdout.write(self.style.SUCCESS('Created instructor'))
        
        # Create courses
        courses_data = [
            {
                'title': 'Complete Python Web Development',
                'description': 'Master Python web development with Django and Flask. Build real-world applications from scratch.',
                'short_description': 'Learn to build modern web applications with Python',
                'level': 'beginner',
                'price': 99.99,
                'duration_hours': 40,
                'category': categories[0],
                'featured': True,
            },
            {
                'title': 'Advanced Data Science with Python',
                'description': 'Deep dive into data science, machine learning, and AI. Learn pandas, numpy, scikit-learn, and more.',
                'short_description': 'Advanced techniques for data analysis and ML',
                'level': 'advanced',
                'price': 149.99,
                'duration_hours': 60,
                'category': categories[1],
                'featured': True,
            },
            {
                'title': 'React Native Mobile Development',
                'description': 'Build cross-platform mobile apps with React Native. Create iOS and Android apps efficiently.',
                'short_description': 'Create iOS and Android apps with one codebase',
                'level': 'intermediate',
                'price': 119.99,
                'duration_hours': 50,
                'category': categories[2],
                'featured': False,
            },
            {
                'title': 'JavaScript Mastery: From Beginner to Advanced',
                'description': 'Complete JavaScript course covering ES6+, async programming, and modern frameworks.',
                'short_description': 'Master JavaScript from basics to advanced concepts',
                'level': 'beginner',
                'price': 89.99,
                'duration_hours': 45,
                'category': categories[4],
                'featured': True,
            },
            {
                'title': 'Django REST Framework API Development',
                'description': 'Build powerful REST APIs with Django REST Framework. Learn authentication, serializers, and more.',
                'short_description': 'Create robust REST APIs with Django',
                'level': 'intermediate',
                'price': 129.99,
                'duration_hours': 35,
                'category': categories[0],
                'featured': False,
            },
            {
                'title': 'UI/UX Design Fundamentals',
                'description': 'Learn the principles of user interface and user experience design. Create beautiful and functional designs.',
                'short_description': 'Master the fundamentals of UI/UX design',
                'level': 'beginner',
                'price': 79.99,
                'duration_hours': 30,
                'category': categories[3],
                'featured': True,
            },
            {
                'title': 'Digital Marketing Complete Course',
                'description': 'Learn SEO, social media marketing, content marketing, and email marketing strategies.',
                'short_description': 'Comprehensive digital marketing strategies',
                'level': 'beginner',
                'price': 94.99,
                'duration_hours': 42,
                'category': categories[6],
                'featured': False,
            },
            {
                'title': 'Machine Learning with TensorFlow',
                'description': 'Build and deploy machine learning models using TensorFlow and Keras.',
                'short_description': 'Deep learning with TensorFlow',
                'level': 'advanced',
                'price': 159.99,
                'duration_hours': 55,
                'category': categories[1],
                'featured': False,
            },
            {
                'title': 'Flutter App Development',
                'description': 'Build beautiful cross-platform mobile apps with Flutter and Dart.',
                'short_description': 'Create stunning mobile apps with Flutter',
                'level': 'intermediate',
                'price': 109.99,
                'duration_hours': 48,
                'category': categories[2],
                'featured': False,
            },
            {
                'title': 'Vue.js Complete Guide',
                'description': 'Master Vue.js framework for building modern web applications. Learn Vue 3, Composition API, and more.',
                'short_description': 'Complete Vue.js framework course',
                'level': 'intermediate',
                'price': 99.99,
                'duration_hours': 38,
                'category': categories[0],
                'featured': False,
            },
            {
                'title': 'Startup Business Fundamentals',
                'description': 'Learn how to start and grow a successful business. Business planning, funding, and marketing.',
                'short_description': 'Essential business skills for entrepreneurs',
                'level': 'beginner',
                'price': 69.99,
                'duration_hours': 25,
                'category': categories[5],
                'featured': False,
            },
            {
                'title': 'Professional Photography Course',
                'description': 'Master photography techniques, composition, lighting, and post-processing.',
                'short_description': 'Become a professional photographer',
                'level': 'beginner',
                'price': 84.99,
                'duration_hours': 32,
                'category': categories[7],
                'featured': False,
            },
        ]
        
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    **course_data,
                    'instructor': instructor,
                    'status': 'published',
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
                
                # Create modules and lessons
                for module_num in range(1, 4):
                    module = Module.objects.create(
                        course=course,
                        title=f'Module {module_num}',
                        description=f'Content for module {module_num}',
                        order=module_num
                    )
                    
                    for lesson_num in range(1, 4):
                        lesson = Lesson.objects.create(
                            module=module,
                            title=f'Lesson {module_num}.{lesson_num}',
                            description=f'Lesson content {module_num}.{lesson_num}',
                            lesson_type='video',
                            order=lesson_num,
                            duration_minutes=30,
                            is_free_preview=(lesson_num == 1)
                        )
                        
                        Content.objects.create(
                            lesson=lesson,
                            content_type='video',
                            video_url=f'https://example.com/video/{course.slug}-{module_num}-{lesson_num}',
                            text_content=f'Video content for lesson {module_num}.{lesson_num}'
                        )
        
        # Create student
        student, created = User.objects.get_or_create(
            email='student@example.com',
            defaults={
                'username': 'student',
                'user_type': 'student',
                'first_name': 'Jane',
                'last_name': 'Smith',
            }
        )
        if created:
            student.set_password('password123')
            student.save()
            self.stdout.write(self.style.SUCCESS('Created student'))
            
            # Enroll student in first course
            course = Course.objects.first()
            if course:
                enrollment = Enrollment.objects.create(
                    student=student,
                    course=course,
                    status='active'
                )
                CourseProgress.objects.create(enrollment=enrollment)
                self.stdout.write(self.style.SUCCESS(f'Enrolled student in: {course.title}'))
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('Instructor: instructor@example.com / password123')
        self.stdout.write('Student: student@example.com / password123')

