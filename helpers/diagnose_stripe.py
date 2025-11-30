"""
Diagnostic Script for Stripe Payment Integration
Run this with: python manage.py shell < diagnose_stripe.py
Or copy-paste into: python manage.py shell
"""

import os
import sys

print("="*60)
print("STRIPE PAYMENT INTEGRATION DIAGNOSTIC")
print("="*60)
print()

# 1. Check Django Settings
print("1. Checking Django Settings...")
try:
    from django.conf import settings
    print("   ✅ Django settings loaded")
    
    # Check DEBUG mode
    print(f"   DEBUG mode: {settings.DEBUG}")
    
    # Check if payments app is installed
    if 'payments' in settings.INSTALLED_APPS:
        print("   ✅ 'payments' app is in INSTALLED_APPS")
    else:
        print("   ❌ 'payments' app is NOT in INSTALLED_APPS")
        print("   -> Add 'payments' to INSTALLED_APPS in settings.py")
    
except Exception as e:
    print(f"   ❌ Error loading settings: {e}")
    sys.exit(1)

print()

# 2. Check Stripe Configuration
print("2. Checking Stripe Configuration...")
try:
    # Check if attributes exist
    if hasattr(settings, 'STRIPE_SECRET_KEY'):
        if settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY != '':
            print(f"   ✅ STRIPE_SECRET_KEY is set (starts with: {settings.STRIPE_SECRET_KEY[:10]}...)")
        else:
            print("   ❌ STRIPE_SECRET_KEY is empty or not set")
            print("   -> Add STRIPE_SECRET_KEY to your .env file")
    else:
        print("   ❌ STRIPE_SECRET_KEY not found in settings")
        print("   -> Add this to settings.py:")
        print("      STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')")
    
    if hasattr(settings, 'STRIPE_PUBLISHABLE_KEY'):
        if settings.STRIPE_PUBLISHABLE_KEY and settings.STRIPE_PUBLISHABLE_KEY != '':
            print(f"   ✅ STRIPE_PUBLISHABLE_KEY is set (starts with: {settings.STRIPE_PUBLISHABLE_KEY[:10]}...)")
        else:
            print("   ❌ STRIPE_PUBLISHABLE_KEY is empty or not set")
    else:
        print("   ❌ STRIPE_PUBLISHABLE_KEY not found in settings")
    
    if hasattr(settings, 'STRIPE_WEBHOOK_SECRET'):
        if settings.STRIPE_WEBHOOK_SECRET and settings.STRIPE_WEBHOOK_SECRET != '':
            print(f"   ✅ STRIPE_WEBHOOK_SECRET is set (starts with: {settings.STRIPE_WEBHOOK_SECRET[:10]}...)")
        else:
            print("   ⚠️  STRIPE_WEBHOOK_SECRET is empty (OK for now, needed for webhooks)")
    else:
        print("   ⚠️  STRIPE_WEBHOOK_SECRET not found in settings (OK for initial testing)")
        
except Exception as e:
    print(f"   ❌ Error checking Stripe config: {e}")

print()

# 3. Test Stripe Connection
print("3. Testing Stripe Connection...")
try:
    import stripe
    print("   ✅ stripe package is installed")
    
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Try to make a test API call
        balance = stripe.Balance.retrieve()
        print("   ✅ Successfully connected to Stripe API!")
        print(f"   Account currency: {balance.available[0].currency if balance.available else 'N/A'}")
        
    except stripe.error.AuthenticationError:
        print("   ❌ Stripe authentication failed - check your STRIPE_SECRET_KEY")
        print("   -> Get your keys from: https://dashboard.stripe.com/test/apikeys")
    except Exception as e:
        print(f"   ❌ Stripe connection error: {e}")
        
except ImportError:
    print("   ❌ stripe package is NOT installed")
    print("   -> Run: pip install stripe")

print()

# 4. Check Payment Models
print("4. Checking Payment Models...")
try:
    from payments.models import Payment, StripeWebhookEvent
    print("   ✅ Payment models imported successfully")
    
    # Check if tables exist
    payment_count = Payment.objects.count()
    print(f"   ✅ Payment table exists ({payment_count} records)")
    
    webhook_count = StripeWebhookEvent.objects.count()
    print(f"   ✅ StripeWebhookEvent table exists ({webhook_count} records)")
    
except ImportError:
    print("   ❌ Cannot import payment models")
    print("   -> Make sure payments app exists and is in INSTALLED_APPS")
except Exception as e:
    print(f"   ❌ Database error: {e}")
    print("   -> Run: python manage.py makemigrations payments")
    print("   -> Run: python manage.py migrate")

print()

# 5. Check Course Model
print("5. Checking Course Model...")
try:
    from courses.models import Course
    print("   ✅ Course model imported successfully")
    
    # Try to get the specific course
    course_slug = 'advanced-data-science-with-python'
    course = Course.objects.filter(slug=course_slug).first()
    
    if course:
        print(f"   ✅ Course found: {course.title}")
        print(f"      - Slug: {course.slug}")
        print(f"      - Price: ${course.price}")
        print(f"      - Status: {course.status}")
        
        # Check required attributes
        required_attrs = ['title', 'slug', 'price', 'status']
        for attr in required_attrs:
            if hasattr(course, attr):
                value = getattr(course, attr)
                print(f"      - {attr}: ✅ ({value})")
            else:
                print(f"      - {attr}: ❌ MISSING")
        
        # Check optional attributes
        if hasattr(course, 'thumbnail'):
            print(f"      - thumbnail: ✅")
        else:
            print(f"      - thumbnail: ⚠️  (optional)")
            
        if hasattr(course, 'short_description'):
            print(f"      - short_description: ✅")
        else:
            print(f"      - short_description: ⚠️  (optional)")
    else:
        print(f"   ❌ Course not found with slug: {course_slug}")
        print("   -> Create a course with this slug or use a different slug")
        
        # Show available courses
        courses = Course.objects.all()[:5]
        if courses:
            print("\n   Available courses:")
            for c in courses:
                print(f"      - {c.slug} ({c.title})")
    
except ImportError:
    print("   ❌ Cannot import Course model")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 6. Check User Model
print("6. Checking User Model...")
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("   ✅ User model loaded")
    
    user = User.objects.first()
    if user:
        print(f"   ✅ Test user found: {user.username}")
        
        # Check email
        if hasattr(user, 'email') and user.email:
            print(f"      - Email: {user.email}")
        else:
            print(f"      - Email: ⚠️  Not set (optional but recommended)")
            
    else:
        print("   ⚠️  No users found in database")
        print("   -> Create a user to test with")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 7. Check Enrollment Model
print("7. Checking Enrollment Model...")
try:
    from enrollments.models import Enrollment
    print("   ✅ Enrollment model imported successfully")
    
    enrollment_count = Enrollment.objects.count()
    print(f"   ✅ Enrollment table exists ({enrollment_count} records)")
    
except ImportError:
    print("   ❌ Cannot import Enrollment model")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 8. Summary
print("="*60)
print("SUMMARY")
print("="*60)

all_good = True

# Check critical items
critical_checks = []

try:
    if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
        critical_checks.append("❌ STRIPE_SECRET_KEY not configured")
        all_good = False
    
    if 'payments' not in settings.INSTALLED_APPS:
        critical_checks.append("❌ 'payments' not in INSTALLED_APPS")
        all_good = False
    
    try:
        from payments.models import Payment
    except:
        critical_checks.append("❌ Payment models not migrated")
        all_good = False
    
    if critical_checks:
        print("\n⚠️  CRITICAL ISSUES FOUND:")
        for check in critical_checks:
            print(f"   {check}")
        print("\nFIX THESE FIRST!")
    else:
        print("\n✅ All critical checks passed!")
        print("\nYou should be able to process payments now.")
        print("If you still get errors, check the full traceback in Django logs.")
        
except Exception as e:
    print(f"\n❌ Error in summary: {e}")

print()
print("="*60)
print("\nNext steps:")
print("1. Fix any ❌ issues shown above")
print("2. Restart your Django server")
print("3. Try the checkout again")
print("4. If still errors, check Django server logs for detailed traceback")
print("="*60)