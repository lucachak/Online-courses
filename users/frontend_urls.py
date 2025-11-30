from django.urls import path
from . import frontend_views

urlpatterns = [
    path('settings/', frontend_views.user_settings, name='user_settings'),
    path('settings/professor/', frontend_views.professor_settings, name='professor_settings'),
    path('settings/admin/', frontend_views.admin_settings, name='admin_settings'),
]

