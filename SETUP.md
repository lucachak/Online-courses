# Setup Instructions

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Database Setup**
   ```bash
   # For SQLite (development)
   # Set USE_SQLITE=True in .env
   
   # For PostgreSQL (production)
   # Set database credentials in .env
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

5. **Setup Tailwind CSS**
   ```bash
   cd theme/static_src
   npm install
   npm run build  # or npm run watch for development
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create Sample Data (Optional)**
   ```bash
   python manage.py create_sample_data
   ```

8. **Run Server**
   ```bash
   python manage.py runserver
   ```

## Features Implemented

✅ Custom User Model with Student/Instructor/Admin roles
✅ Course Management (Courses, Modules, Lessons, Content)
✅ Category System
✅ Enrollment and Progress Tracking
✅ Django REST Framework APIs
✅ Django Allauth Authentication
✅ Django Tailwind CSS Theme
✅ Django Unfold Modern Admin
✅ Django Browser Reload
✅ Beautiful Frontend Templates
✅ Horizontal Course Tray UI
✅ Responsive Design
✅ PostgreSQL Support
✅ Sample Data Management Command

## Next Steps

1. Customize the Tailwind theme in `theme/static_src/src/input.css`
2. Add more course categories
3. Configure social authentication in allauth settings
4. Set up email backend for account verification
5. Configure production server (nginx, gunicorn)

## Troubleshooting

**Port 8000 already in use:**
```bash
# Stop all Django/Tailwind servers
./stop_server.sh

# Or manually kill processes
pkill -f "python.*manage.py.*runserver"
lsof -ti:8000 | xargs kill -9
```

**Tailwind CSS not working:**
- Make sure you've run `npm install` in `theme/static_src/`
- Run `npm run build` or `npm run watch`
- Check that `theme` app is in INSTALLED_APPS
- Ensure `start` script exists in `theme/static_src/package.json`

**Database errors:**
- Check your database credentials in `.env`
- Make sure PostgreSQL is running (if using PostgreSQL)
- Or set `USE_SQLITE=True` for development

**Static files not loading:**
- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL in settings
- Ensure WhiteNoise is in MIDDLEWARE

