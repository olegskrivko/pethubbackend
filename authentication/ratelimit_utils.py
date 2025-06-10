from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from functools import wraps
# from django.contrib.auth import get_user_model
# User = get_user_model()


# Global default: limit to 100 requests per hour per IP address, block if exceeded
default_rate_limit = ratelimit(key='ip', rate='100/h', block=True)
forgot_password_rate_limit = ratelimit(key='ip', rate='3/m', block=True) 

from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from functools import wraps

def ratelimit_with_custom_response(key='ip', rate='3/m', method='POST', block=False):
    def decorator(view_func):
        @ratelimit(key=key, rate=rate, method=method, block=block)
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not block and getattr(request, 'limited', False):
                return JsonResponse({"error": "Rate limit exceeded. Try again later."}, status=429)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


register_rate_limit = ratelimit_with_custom_response(rate='3/m', method='POST', block=False)
login_rate_limit = ratelimit_with_custom_response(rate='5/m', method='POST', block=False)
activate_rate_limit = ratelimit_with_custom_response(rate='5/m', method='GET', block=False)
feedback_rate_limit = ratelimit_with_custom_response(rate='5/m', method='POST', block=False)

test_rate_limit = ratelimit_with_custom_response(rate='3/m', method='GET', block=False)
# The decorator ratelimit automatically tracks requests per the key (here IP address) and rate.

# block=True will return HTTP 429 response automatically if rate limit exceeded.

# You can create as many custom rate limits as you want for specific endpoints.






# 🔐 Auth Routes (Sensitive)
# These are common targets for abuse (e.g., brute-force, spam), so they need tighter limits:

# Endpoint	Recommended Limit	Notes
# Login	5/min/IP	Blocks brute-force attempts. Consider CAPTCHA after multiple failures.
# Register	3/min/IP	Prevents bot-driven account creation. Optionally add CAPTCHA.
# Forgot Password	3/min/IP	Prevents abuse of password reset. You may also limit per email.
# Activate Account	10/min/IP	Less critical, but don’t allow spamming.
# Resend Verification Email	2/min/IP	Prevent user abuse. Maybe 1/min is even safer.

# 🌐 Public Routes (No Auth Required)
# These need moderate protection against scraping, spamming, or abuse:

# Endpoint	Recommended Limit	Notes
# Public API endpoints (e.g., listing posts, public profiles)	60/min/IP or 100/hour/IP	Adjust based on traffic.
# Search	10/min/IP	Scraping risk is high. Add caching or debounce client-side.

# 🔒 Authenticated Routes (User-Specific)
# These are safer, but still benefit from basic rate-limiting:

# Endpoint	Recommended Limit	Notes
# Profile Updates / Settings	10/hour/user	Prevent abuse or accidental rapid requests.
# Create Content (posts/comments/etc.)	5/min/user	Avoid spammy behavior.
# Fetch Own Data	100/min/user or more	Often OK to be lenient here.
# Any heavy task (e.g., file uploads)	2/min/user	Prevent resource exhaustion.








