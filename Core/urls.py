from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin (Django Unfold)
    path("admin/", admin.site.urls),
    # Allauth URLs
    path("accounts/", include("allauth.urls")),
    # API URLs
    path("api/auth/", include("rest_framework.urls")),
    path("api/users/", include("users.urls")),
    path("api/courses/", include("courses.urls")),
    path("api/enrollments/", include("enrollments.urls")),
    # Payments URLs
    path("payments/", include("payments.urls")),
    # Frontend views
    path("", include("courses.frontend_urls")),
    path("", include("users.frontend_urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Browser reload
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
