<<<<<<< HEAD
# Online-courses
=======
# Django Course Platform

A production-ready Django course platform similar to Coursera/Udemy with modern UI, REST APIs, and comprehensive course management.

## Features

- **User Management**: Student, Instructor, and Admin roles with custom user model
- **Course Management**: Courses with modules, lessons, and content
- **Progress Tracking**: Enrollment and lesson completion tracking
- **Beautiful UI**: Modern Tailwind CSS design with horizontal course tray
- **REST APIs**: Complete API with Django REST Framework
- **Authentication**: Django Allauth with email-based login
- **Modern Admin**: Django Unfold for beautiful admin interface
- **Auto-reload**: Django Browser Reload for development

## Tech Stack

- Django 5.2+
- Django REST Framework
- Django Allauth & Allauth UI
- Django Tailwind CSS
- Django Unfold (Admin)
- PostgreSQL (with SQLite fallback)
- WhiteNoise (Static files)

## Installation

### 1. Clone and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env with your settings
```

### 2. Database Setup

**Option A: PostgreSQL (Recommended for Production)**
```bash
# Update .env with your PostgreSQL credentials
DB_NAME=course_platform
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
USE_SQLITE=False
```

**Option B: SQLite (Development)**
```bash
# In .env file
USE_SQLITE=True
```

### 3. Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Setup Tailwind CSS

```bash
# Install Tailwind dependencies
cd theme/static_src
npm install

# Build CSS (for production)
npm run build

# Watch mode (for development)
npm run watch
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Create Sample Data (Optional)

```bash
python manage.py create_sample_data
```

This creates:
- Sample categories
- Sample courses with modules and lessons
- Test instructor (instructor@example.com / password123)
- Test student (student@example.com / password123)

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit:
- Home: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/

## Project Structure

```
course_platform/
├── Core/              # Django project settings
├── users/             # User management app
├── courses/           # Course content app
├── enrollments/       # Progress tracking app
├── theme/             # Tailwind CSS theme
├── templates/         # HTML templates
├── static/            # Static files
└── media/             # Media files (user uploads)
```

## API Endpoints

### Authentication
- `POST /api/users/users/` - Register new user
- `GET /api/users/users/me/` - Get current user
- `PUT /api/users/users/update_profile/` - Update profile

### Courses
- `GET /api/courses/courses/` - List courses
- `GET /api/courses/courses/{id}/` - Course detail
- `POST /api/courses/courses/` - Create course (instructor)
- `GET /api/courses/categories/` - List categories

### Enrollments
- `GET /api/enrollments/enrollments/` - User enrollments
- `POST /api/enrollments/enrollments/` - Enroll in course
- `GET /api/enrollments/enrollments/{id}/progress/` - Enrollment progress

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated host list
- Database configuration (DB_NAME, DB_USER, etc.)
- `CORS_ALLOWED_ORIGINS` - CORS origins

## Development

### Running with Auto-reload

The project includes `django-browser-reload` for automatic browser refresh during development. Just run the server and changes will automatically reload.

### Tailwind CSS Development

```bash
# In theme/static_src/
npm run watch
```

This watches for changes and rebuilds CSS automatically.

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Set proper `ALLOWED_HOSTS`
3. Configure PostgreSQL database
4. Set strong `SECRET_KEY`
5. Run `collectstatic`
6. Configure web server (nginx/Apache)
7. Use Gunicorn or uWSGI for WSGI

## License

MIT License

>>>>>>> 5d962da (Starting point)
