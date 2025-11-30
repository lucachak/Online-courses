import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from courses.models import Course
from enrollments.models import Enrollment
from .models import Payment, StripeWebhookEvent
import traceback
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Stripe
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if not stripe.api_key or stripe.api_key == '':
        logger.error("STRIPE_SECRET_KEY is not set in settings!")
except AttributeError:
    logger.error("STRIPE_SECRET_KEY not found in settings!")
    stripe.api_key = None


@login_required
def create_checkout_session(request, course_slug):
    """Create a Stripe checkout session for a course"""
    try:
        # Check if Stripe is configured
        if not stripe.api_key or stripe.api_key == '':
            messages.error(request, 'Payment system is not configured. Please contact administrator.')
            logger.error("Stripe API key not configured")
            return redirect('course_detail', slug=course_slug)
        
        # Get course
        try:
            course = get_object_or_404(Course, slug=course_slug, status='published')
        except Exception as e:
            logger.error(f"Course not found: {course_slug} - {str(e)}")
            messages.error(request, 'Course not found.')
            return redirect('home')
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.info(request, 'You are already enrolled in this course.')
            return redirect('course_detail', slug=course_slug)
        
        # Check if there's a pending payment
        pending_payment = Payment.objects.filter(
            user=request.user,
            course=course,
            status='pending'
        ).first()
        
        if pending_payment and pending_payment.stripe_checkout_session_id:
            # Retrieve existing session
            try:
                session = stripe.checkout.Session.retrieve(
                    pending_payment.stripe_checkout_session_id
                )
                if session.status == 'open':
                    return redirect(session.url)
            except stripe.error.StripeError as e:
                logger.error(f"Error retrieving Stripe session: {str(e)}")
                pass
        
        # Create new payment record
        try:
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                currency='USD',
                status='pending'
            )
        except Exception as e:
            logger.error(f"Error creating payment record: {str(e)}")
            messages.error(request, 'Error creating payment. Please try again.')
            return redirect('course_detail', slug=course_slug)
        
        # Prepare product images
        product_images = []
        if hasattr(course, 'thumbnail') and course.thumbnail:
            try:
                thumbnail_url = request.build_absolute_uri(course.thumbnail.url)
                product_images = [thumbnail_url]
            except Exception as e:
                logger.warning(f"Error getting thumbnail URL: {str(e)}")
                product_images = []
        
        # Prepare description
        description = ''
        if hasattr(course, 'short_description') and course.short_description:
            description = course.short_description
        elif hasattr(course, 'description') and course.description:
            description = course.description[:200] if len(course.description) > 200 else course.description
        
        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(float(course.price) * 100),  # Convert to cents
                        'product_data': {
                            'name': course.title,
                            'description': description,
                            'images': product_images,
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(
                    reverse('payments:payment_success')
                ) + f'?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=request.build_absolute_uri(
                    reverse('payments:payment_cancel', args=[course_slug])
                ),
                metadata={
                    'payment_id': payment.id,
                    'user_id': request.user.id,
                    'course_id': course.id,
                },
                customer_email=request.user.email if hasattr(request.user, 'email') else None,
            )
            
            # Update payment with session ID
            payment.stripe_checkout_session_id = checkout_session.id
            payment.save()
            
            # Redirect to Stripe checkout
            return redirect(checkout_session.url)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            messages.error(request, f'Payment error: {str(e)}')
            payment.status = 'failed'
            payment.save()
            return redirect('course_detail', slug=course_slug)
        except Exception as e:
            logger.error(f"Unexpected error creating checkout session: {str(e)}")
            logger.error(traceback.format_exc())
            messages.error(request, f'Unexpected error: {str(e)}')
            payment.status = 'failed'
            payment.save()
            return redirect('course_detail', slug=course_slug)
            
    except Exception as e:
        logger.error(f"Fatal error in create_checkout_session: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, 'An error occurred. Please try again later.')
        return redirect('home')


@login_required
def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('home')
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Get payment record
        payment = Payment.objects.filter(
            stripe_checkout_session_id=session_id
        ).first()
        
        if not payment:
            messages.error(request, 'Payment record not found.')
            return redirect('home')
        
        # Update payment status
        if session.payment_status == 'paid' and payment.status != 'completed':
            payment.status = 'completed'
            payment.stripe_payment_intent_id = session.payment_intent
            payment.completed_at = timezone.now()
            payment.save()
            
            # Create enrollment
            enrollment, created = Enrollment.objects.get_or_create(
                student=payment.user,
                course=payment.course,
                defaults={'status': 'active'}
            )
            
            if created:
                messages.success(
                    request,
                    f'Payment successful! You are now enrolled in {payment.course.title}.'
                )
            else:
                messages.info(request, 'You are already enrolled in this course.')
            
            return render(request, 'payments/success.html', {
                'payment': payment,
                'course': payment.course,
                'enrollment': enrollment,
            })
        else:
            messages.warning(request, 'Payment is being processed.')
            return redirect('course_detail', slug=payment.course.slug)
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error in payment_success: {str(e)}")
        messages.error(request, f'Error verifying payment: {str(e)}')
        return redirect('home')
    except Exception as e:
        logger.error(f"Error in payment_success: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, 'An error occurred while processing your payment.')
        return redirect('home')


@login_required
def payment_cancel(request, course_slug):
    """Handle cancelled payment"""
    try:
        course = get_object_or_404(Course, slug=course_slug)
        
        # Update any pending payments
        Payment.objects.filter(
            user=request.user,
            course=course,
            status='pending'
        ).update(status='failed')
        
        messages.info(request, 'Payment was cancelled. You can try again when ready.')
        
        return render(request, 'payments/cancel.html', {
            'course': course,
        })
    except Exception as e:
        logger.error(f"Error in payment_cancel: {str(e)}")
        messages.error(request, 'An error occurred.')
        return redirect('home')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        return HttpResponse(status=400)
    except AttributeError as e:
        logger.error(f"STRIPE_WEBHOOK_SECRET not configured: {str(e)}")
        return HttpResponse(status=400)
    
    # Store webhook event
    try:
        webhook_event, created = StripeWebhookEvent.objects.get_or_create(
            event_id=event['id'],
            defaults={
                'event_type': event['type'],
                'payload': event,
            }
        )
        
        if not created:
            # Event already processed
            return HttpResponse(status=200)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_checkout_session_completed(session)
        
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            handle_payment_intent_succeeded(payment_intent)
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            handle_payment_intent_failed(payment_intent)
        
        # Mark as processed
        webhook_event.processed = True
        webhook_event.save()
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        logger.error(traceback.format_exc())
    
    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Process completed checkout session"""
    try:
        payment = Payment.objects.filter(
            stripe_checkout_session_id=session['id']
        ).first()
        
        if not payment:
            logger.warning(f"Payment not found for session: {session['id']}")
            return
        
        if session['payment_status'] == 'paid':
            payment.status = 'completed'
            payment.stripe_payment_intent_id = session.get('payment_intent')
            payment.completed_at = timezone.now()
            payment.save()
            
            # Create enrollment if it doesn't exist
            Enrollment.objects.get_or_create(
                student=payment.user,
                course=payment.course,
                defaults={'status': 'active'}
            )
    except Exception as e:
        logger.error(f"Error in handle_checkout_session_completed: {str(e)}")


def handle_payment_intent_succeeded(payment_intent):
    """Process successful payment intent"""
    try:
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent['id']
        ).first()
        
        if payment and payment.status != 'completed':
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
    except Exception as e:
        logger.error(f"Error in handle_payment_intent_succeeded: {str(e)}")


def handle_payment_intent_failed(payment_intent):
    """Process failed payment intent"""
    try:
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent['id']
        ).first()
        
        if payment:
            payment.status = 'failed'
            payment.save()
    except Exception as e:
        logger.error(f"Error in handle_payment_intent_failed: {str(e)}")


@login_required
def payment_history(request):
    """View payment history"""
    try:
        payments = Payment.objects.filter(user=request.user).select_related('course')
        
        return render(request, 'payments/history.html', {
            'payments': payments,
        })
    except Exception as e:
        logger.error(f"Error in payment_history: {str(e)}")
        messages.error(request, 'Error loading payment history.')
        return redirect('home')