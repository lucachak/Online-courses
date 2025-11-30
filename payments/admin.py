from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment, StripeWebhookEvent


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ['id', 'user', 'course', 'amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'currency']
    search_fields = ['user__username', 'user__email', 'course__title', 'stripe_checkout_session_id']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'stripe_checkout_session_id', 'stripe_payment_intent_id']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'course', 'amount', 'currency', 'status')
        }),
        ('Stripe Details', {
            'fields': ('stripe_checkout_session_id', 'stripe_payment_intent_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Payments should only be created through the payment flow
        return False


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(ModelAdmin):
    list_display = ['event_id', 'event_type', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'event_type']
    readonly_fields = ['event_id', 'event_type', 'payload', 'processed', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False