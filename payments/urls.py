from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:course_slug>/', views.create_checkout_session, name='checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/<slug:course_slug>/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('history/', views.payment_history, name='payment_history'),
]