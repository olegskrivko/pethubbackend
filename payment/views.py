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
def create_subscription_session(request):
    user = request.user
    subscription_type = request.data.get('subscription_type', 'plus')
    
    if subscription_type not in settings.STRIPE_SUBSCRIPTION_PRICE_IDS:
        return Response(
            {"error": f"Invalid subscription type. Must be one of: {', '.join(settings.STRIPE_SUBSCRIPTION_PRICE_IDS.keys())}"}, 
            status=400
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user.email,
            line_items=[
                {
                    "price": settings.STRIPE_SUBSCRIPTION_PRICE_IDS[subscription_type],
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=f"{settings.DOMAIN_APP_URL}/subscription-success",
            cancel_url=f"{settings.DOMAIN_APP_URL}/subscription-cancel",
            metadata={
                "subscription_type": subscription_type,
                "user_id": user.id
            }
        )
        return Response({"url": checkout_session.url})
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        return Response({"error": "An unexpected error occurred"}, status=500)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, 
            sig_header, 
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return Response({"error": "Invalid signature"}, status=400)

    try:
        if event.type == 'checkout.session.completed':
            session = event.data.object
            handle_checkout_session_completed(session)
        elif event.type == 'customer.subscription.updated':
            subscription = event.data.object
            handle_subscription_updated(subscription)
        elif event.type == 'customer.subscription.deleted':
            subscription = event.data.object
            handle_subscription_deleted(subscription)
            
        return Response(status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

def handle_checkout_session_completed(session):
    customer_email = session.get('customer_email')
    subscription_type = session.get('metadata', {}).get('subscription_type', 'plus')

    try:
        user = User.objects.get(email=customer_email)
        user.is_subscribed = True
        user.subscription_start = timezone.now()
        user.stripe_customer_id = session.get('customer')
        user.subscription_type = subscription_type
        user.save()
    except User.DoesNotExist:
        pass

def handle_subscription_updated(subscription):
    customer_id = subscription.get('customer')
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        user.subscription_type = subscription.get('metadata', {}).get('subscription_type', 'plus')
        user.save()
    except User.DoesNotExist:
        pass

def handle_subscription_deleted(subscription):
    customer_id = subscription.get('customer')
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        user.is_subscribed = False
        user.subscription_type = None
        user.save()
    except User.DoesNotExist:
        pass


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_one_time_payment_session(request):
#     user = request.user

#     try:
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             customer_email=user.email,
#             line_items=[
#                 {
#                     "price_data": {
#                         "currency": "usd",
#                         "product_data": {
#                             "name": "One-Time Service",
#                         },
#                         "unit_amount": 1000,  # $10.00
#                     },
#                     "quantity": 1,
#                 }
#             ],
#             mode="payment",  # 👈 One-time payment mode
#             success_url=f"{DOMAIN_APP_URL}/payment-success",
#             cancel_url=f"{DOMAIN_APP_URL}/payment-cancel",
#         )
#         return JsonResponse({"url": checkout_session.url})
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_subscription_session(request):
#     user = request.user

#     try:
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             customer_email=user.email,
#             line_items=[
#                 {
#                     "price": settings.STRIPE_SUBSCRIPTION_PRICE_ID,  # Predefined recurring price ID
#                     "quantity": 1,
#                 }
#             ],
#             mode="subscription",  # 👈 Subscription mode
#             success_url=f"{DOMAIN_APP_URL}/subscription-success",
#             cancel_url=f"{DOMAIN_APP_URL}/subscription-cancel",
#         )
#         return JsonResponse({"url": checkout_session.url})
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)



# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.headers.get("Stripe-Signature")
    
#     # Verify the signature to ensure the request is from Stripe
#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#     except ValueError as e:
#         print(f"Invalid payload: {str(e)}")
#         return HttpResponse("Invalid payload", status=400)
#     except stripe.error.SignatureVerificationError as e:
#         print(f"Signature verification failed: {str(e)}")
#         return HttpResponse("Signature verification failed", status=400)

#     # Process the event
#     event_type = event.get('type')
#     if event_type == 'checkout.session.completed':
#         session = event['data']['object']
#         customer_email = session.get('customer_email')

#         # Handle subscription mode
#         if session['mode'] == 'subscription':
#             try:
#                 user = User.objects.get(email=customer_email)
#                 user.is_subscribed = True
#                 user.subscription_start = timezone.now()
#                 user.stripe_customer_id = session.get('customer')  # Save customer ID
#                 user.subscription_type = "premium"  # Or derive from metadata or plan name
#                 user.save()
#                 print(f"User {user.email} subscribed successfully.")
#             except User.DoesNotExist:
#                 print(f"User with email {customer_email} not found.")

#         # Handle one-time payment mode
#         elif session['mode'] == 'payment':
#             print(f"One-time payment completed by {customer_email}")

#     # Handle other event types if necessary
#     else:
#         print(f"Unhandled event type: {event_type}")

#     return HttpResponse(status=200)  # Respond to acknowledge the event



### NEW
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_subscription_session(request):
#     user = request.user
#     subscription_type = request.data.get('subscription_type', 'plus')  # Default to 'plus' if not specified
    
#     if subscription_type not in settings.STRIPE_SUBSCRIPTION_PRICE_IDS:
#         return Response({"error": "Invalid subscription type"}, status=400)

#     try:
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             customer_email=user.email,
#             line_items=[
#                 {
#                     "price": settings.STRIPE_SUBSCRIPTION_PRICE_IDS[subscription_type],
#                     "quantity": 1,
#                 }
#             ],
#             mode="subscription",
#             success_url=f"{DOMAIN_APP_URL}/subscription-success",
#             cancel_url=f"{DOMAIN_APP_URL}/subscription-cancel",
#             metadata={
#                 "subscription_type": subscription_type,  # Add metadata to track subscription type
#                 "user_id": user.id
#             }
#         )
#         return JsonResponse({"url": checkout_session.url})
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)


# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.headers.get("Stripe-Signature")
    
#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#     except ValueError as e:
#         print(f"Invalid payload: {str(e)}")
#         return HttpResponse("Invalid payload", status=400)
#     except stripe.error.SignatureVerificationError as e:
#         print(f"Signature verification failed: {str(e)}")
#         return HttpResponse("Signature verification failed", status=400)

#     event_type = event.get('type')
    
#     if event_type == 'checkout.session.completed':
#         session = event['data']['object']
#         customer_email = session.get('customer_email')
#         subscription_type = session.get('metadata', {}).get('subscription_type', 'plus')

#         if session['mode'] == 'subscription':
#             try:
#                 user = User.objects.get(email=customer_email)
#                 user.is_subscribed = True
#                 user.subscription_start = timezone.now()
#                 user.stripe_customer_id = session.get('customer')
#                 user.subscription_type = subscription_type  # Use the subscription type from metadata
#                 user.save()
#                 print(f"User {user.email} subscribed to {subscription_type} tier successfully.")
#             except User.DoesNotExist:
#                 print(f"User with email {customer_email} not found.")

#     elif event_type == 'customer.subscription.updated':
#         # Handle subscription updates (e.g., plan changes)
#         subscription = event['data']['object']
#         customer_id = subscription.get('customer')
#         try:
#             user = User.objects.get(stripe_customer_id=customer_id)
#             # Update subscription status based on the new plan
#             user.subscription_type = subscription.get('metadata', {}).get('subscription_type', 'plus')
#             user.save()
#         except User.DoesNotExist:
#             print(f"User with customer ID {customer_id} not found.")

#     elif event_type == 'customer.subscription.deleted':
#         # Handle subscription cancellations
#         subscription = event['data']['object']
#         customer_id = subscription.get('customer')
#         try:
#             user = User.objects.get(stripe_customer_id=customer_id)
#             user.is_subscribed = False
#             user.subscription_type = None
#             user.save()
#         except User.DoesNotExist:
#             print(f"User with customer ID {customer_id} not found.")

#     return HttpResponse(status=200)