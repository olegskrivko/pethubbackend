# payment link


from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.http import JsonResponse
from django.utils import timezone
import os
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY  # Use your secret key
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
# print("aaaaa", stripe.api_key)
DOMAIN_APP_URL = os.getenv("DOMAIN_APP_URL")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_one_time_payment_session(request):
    user = request.user

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user.email,
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "One-Time Service",
                        },
                        "unit_amount": 1000,  # $10.00
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",  # 👈 One-time payment mode
            success_url=f"{DOMAIN_APP_URL}/payment-success",
            cancel_url=f"{DOMAIN_APP_URL}/payment-cancel",
        )
        return JsonResponse({"url": checkout_session.url})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_subscription_session(request):
    user = request.user

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user.email,
            line_items=[
                {
                    "price": settings.STRIPE_SUBSCRIPTION_PRICE_ID,  # Predefined recurring price ID
                    "quantity": 1,
                }
            ],
            mode="subscription",  # 👈 Subscription mode
            success_url=f"{DOMAIN_APP_URL}/subscription-success",
            cancel_url=f"{DOMAIN_APP_URL}/subscription-cancel",
        )
        return JsonResponse({"url": checkout_session.url})
    except Exception as e:
        return Response({"error": str(e)}, status=400)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")
    
    # Verify the signature to ensure the request is from Stripe
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        print(f"Invalid payload: {str(e)}")
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Signature verification failed: {str(e)}")
        return HttpResponse("Signature verification failed", status=400)

    # Process the event
    event_type = event.get('type')
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email')

        # Handle subscription mode
        if session['mode'] == 'subscription':
            try:
                user = User.objects.get(email=customer_email)
                user.is_subscribed = True
                user.subscription_start = timezone.now()
                user.stripe_customer_id = session.get('customer')  # Save customer ID
                user.subscription_type = "premium"  # Or derive from metadata or plan name
                user.save()
                print(f"User {user.email} subscribed successfully.")
            except User.DoesNotExist:
                print(f"User with email {customer_email} not found.")

        # Handle one-time payment mode
        elif session['mode'] == 'payment':
            print(f"One-time payment completed by {customer_email}")

    # Handle other event types if necessary
    else:
        print(f"Unhandled event type: {event_type}")

    return HttpResponse(status=200)  # Respond to acknowledge the event