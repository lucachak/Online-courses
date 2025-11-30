from django.urls import path
from . import frontend_views

urlpatterns = [
    path('', frontend_views.home, name='home'),
    path('course/<slug:slug>/', frontend_views.course_detail, name='course_detail'),
    path('courses/', frontend_views.course_list, name='course_list'),
    path('search/', frontend_views.search_courses, name='search_courses'),
]

