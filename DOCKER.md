# Docker Deployment Guide

This guide will help you deploy the Course Platform using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

1. **Clone the repository and navigate to the project directory**

```bash
cd Online-Courses
```

2. **Create a `.env` file** (if you don't have one already):

```bash
cp .env.example .env  # or create manually
```

Make sure your `.env` file contains at least:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1
DB_HOST=db
DB_NAME=course_platform
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
USE_SQLITE=False
```

3. **Build and start the containers**:

```bash
docker-compose up -d --build
```

4. **Run migrations**:

```bash
docker-compose exec web python manage.py migrate
```

5. **Create a superuser** (optional):

```bash
docker-compose exec web python manage.py createsuperuser
```

6. **Collect static files**:

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

7. **Access the application**:

- Web application: http://localhost:8000
- Admin panel: http://localhost:8000/admin
- API: http://localhost:8000/api/

## Production Deployment

For production deployment, you should:

1. **Update environment variables** in `.env`:
   - Set `DEBUG=False`
   - Set a strong `SECRET_KEY`
   - Update `ALLOWED_HOSTS` with your domain
   - Use secure database credentials

2. **Update nginx configuration** (`nginx.conf`):
   - Change `server_name` to your domain
   - Add SSL certificates for HTTPS
   - Configure proper security headers

3. **Build and run**:

```bash
docker-compose -f docker-compose.yml up -d --build
```

## Useful Commands

### View logs
```bash
docker-compose logs -f web
```

### Stop containers
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes database)
```bash
docker-compose down -v
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

### Run management commands
```bash
docker-compose exec web python manage.py <command>
```

### Restart services
```bash
docker-compose restart
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

## Docker Services

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **nginx**: Reverse proxy and static file serving (port 80)

## Troubleshooting

### Database connection issues
- Ensure the database container is healthy: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Verify environment variables match docker-compose.yml

### Static files not loading
- Run collectstatic: `docker-compose exec web python manage.py collectstatic`
- Check nginx configuration
- Verify static volume is mounted correctly

### Permission issues
- Ensure media and static directories have proper permissions
- Check Docker volume permissions

## Notes

- The development setup uses `runserver` for hot reloading
- For production, the Dockerfile uses `gunicorn` (configured in CMD)
- Static and media files are served via nginx in production
- Database data persists in Docker volumes

