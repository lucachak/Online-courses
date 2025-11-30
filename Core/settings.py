import os
from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-8o3ir$octzeu*35k2#u+65$!oq&2$iuc6&2odced1x#f9az18_",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())


# Application definition
INSTALLED_APPS = [
    # Django Unfold Admin
    "unfold",
    "unfold.contrib.filters",
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",
    "widget_tweaks",
    "slippers",
    # Django Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth_ui",
    # Django Tailwind
    "tailwind",
    "theme",
    "django_browser_reload",
    # Local apps
    "users",
    "courses",
    "enrollments",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "Core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Core.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="course_platform"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Fallback to SQLite for development
if config("USE_SQLITE", default=False, cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/staticfiles"),
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# ============================================
# DJANGO-ALLAUTH CONFIGURATION (UPDATED)
# ============================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# AllAuth Account Settings (NEW FORMAT)
ACCOUNT_LOGIN_METHODS = {"username", "email"}  # Users can login with username OR email
ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "username*",
    "password1*",
    "password2*",
]  # Required fields for signup
ACCOUNT_EMAIL_VERIFICATION = "optional"  # 'mandatory', 'optional', or 'none'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_USERNAME_MIN_LENGTH = 4

# AllAuth UI Settings
ALLAUTH_UI_THEME = "auto"

# Social Account Providers
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
            "prompt": "select_account",
        },
        "OAUTH_PKCE_ENABLED": True,
    }
}

# Optional: Custom forms if needed
ACCOUNT_FORMS = {
    "login": "allauth.account.forms.LoginForm",
    "signup": "allauth.account.forms.SignupForm",
    "reset_password": "allauth.account.forms.ResetPasswordForm",
    "reset_password_from_key": "allauth.account.forms.ResetPasswordKeyForm",
    "change_password": "allauth.account.forms.ChangePasswordForm",
}

# Email Configuration
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@yourdomain.com")

# Django Tailwind
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = config(
    "ALLOWED_HOSTS", default="192.168.18.15,localhost,127.0.0.1", cast=Csv()
)

# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# WhiteNoise Configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# Django Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "Course Platform Admin",
    "SITE_HEADER": "Course Platform Administration",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_LOGO": None,
    "SITE_SYMBOL": "school",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Course Management",
                "separator": False,
                "items": [
                    {
                        "title": "Courses",
                        "icon": "book",
                        "link": "/admin/courses/course/",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": "/admin/courses/category/",
                    },
                    {
                        "title": "Modules",
                        "icon": "folder",
                        "link": "/admin/courses/module/",
                    },
                    {
                        "title": "Lessons",
                        "icon": "article",
                        "link": "/admin/courses/lesson/",
                    },
                    {
                        "title": "Content",
                        "icon": "video_file",
                        "link": "/admin/courses/content/",
                    },
                ],
            },
            {
                "title": "User Management",
                "separator": False,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": "/admin/users/user/",
                    },
                    {
                        "title": "Students",
                        "icon": "person",
                        "link": "/admin/users/studentprofile/",
                    },
                    {
                        "title": "Instructors",
                        "icon": "person_pin",
                        "link": "/admin/users/instructorprofile/",
                    },
                ],
            },
            {
                "title": "Enrollments",
                "separator": False,
                "items": [
                    {
                        "title": "Enrollments",
                        "icon": "assignment",
                        "link": "/admin/enrollments/enrollment/",
                    },
                    {
                        "title": "Lesson Progress",
                        "icon": "check_circle",
                        "link": "/admin/enrollments/lessonprogress/",
                    },
                    {
                        "title": "Course Progress",
                        "icon": "trending_up",
                        "link": "/admin/enrollments/courseprogress/",
                    },
                ],
            },
            {
                "title": "Payments",
                "separator": True,
                "items": [
                    {
                        "title": "Payments",
                        "icon": "payment",
                        "link": "/admin/payments/payment/",
                    },
                    {
                        "title": "Webhook Events",
                        "icon": "webhook",
                        "link": "/admin/payments/stripewebhookevent/",
                    },
                ],
            },
            {
                "title": "Authentication",
                "separator": True,
                "items": [
                    {
                        "title": "Social Applications",
                        "icon": "apps",
                        "link": "/admin/socialaccount/socialapp/",
                    },
                    {
                        "title": "Social Accounts",
                        "icon": "account_circle",
                        "link": "/admin/socialaccount/socialaccount/",
                    },
                    {
                        "title": "Social Tokens",
                        "icon": "vpn_key",
                        "link": "/admin/socialaccount/socialtoken/",
                    },
                ],
            },
        ],
    },
}

# ============================================
# STRIPE PAYMENT CONFIGURATION
# ============================================

STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

STRIPE_SUCCESS_URL = config(
    "STRIPE_SUCCESS_URL", default="http://127.0.0.1:8000/payments/success/"
)
STRIPE_CANCEL_URL = config(
    "STRIPE_CANCEL_URL", default="http://127.0.0.1:8000/payments/cancel/"
)

STRIPE_CURRENCY = config("STRIPE_CURRENCY", default="USD")
STRIPE_ENABLED = config("STRIPE_ENABLED", default=True, cast=bool)
