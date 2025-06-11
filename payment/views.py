# payment link


from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

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
        # Invalid payload
        return Response({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return Response({"error": "Invalid signature"}, status=400)

    try:
        # Handle different event types
        if event.type == 'checkout.session.completed':
            session = event.data.object
            handle_checkout_session_completed(session)

        elif event.type == 'customer.subscription.updated':
            subscription = event.data.object
            handle_subscription_updated(subscription)

        elif event.type == 'customer.subscription.deleted':
            subscription = event.data.object
            handle_subscription_deleted(subscription)

        # Add more event types here if needed

        return Response(status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.headers.get("Stripe-Signature")
    
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, 
#             sig_header, 
#             settings.STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError:
#         return Response({"error": "Invalid payload"}, status=400)
#     except stripe.error.SignatureVerificationError:
#         return Response({"error": "Invalid signature"}, status=400)

#     try:
#         if event.type == 'checkout.session.completed':
#             session = event.data.object
#             handle_checkout_session_completed(session)
#         elif event.type == 'customer.subscription.updated':
#             subscription = event.data.object
#             handle_subscription_updated(subscription)
#         elif event.type == 'customer.subscription.deleted':
#             subscription = event.data.object
#             handle_subscription_deleted(subscription)
            
#         return Response(status=200)
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

def handle_checkout_session_completed(session):
    customer_email = session.get('customer_email')
    subscription_type = session.get('metadata', {}).get('subscription_type', 'plus')

    try:
        user = User.objects.get(email=customer_email)
        
        # Get the subscription from the session
        subscription = stripe.Subscription.retrieve(session.subscription)
        
        # Update user's subscription using the new method
        user.update_subscription({
            'customer_id': session.customer,
            'subscription_type': subscription_type,
            'start_date': timezone.now(),
            'end_date': timezone.datetime.fromtimestamp(subscription.current_period_end),
            'is_active': True
        })
        
        print(f"User {user.email} subscribed successfully to {subscription_type} plan")
    except User.DoesNotExist:
        print(f"User with email {customer_email} not found")
    except Exception as e:
        print(f"Error handling checkout session: {str(e)}")

def handle_subscription_updated(subscription):
    customer_id = subscription.get('customer')
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        
        # Update user's subscription using the new method
        user.update_subscription({
            'customer_id': customer_id,
            'subscription_type': subscription.get('metadata', {}).get('subscription_type', 'plus'),
            'start_date': user.subscription_start,  # Keep existing start date
            'end_date': timezone.datetime.fromtimestamp(subscription.current_period_end),
            'is_active': subscription.status == 'active'
        })
        
        print(f"Updated subscription for user {user.email}")
    except User.DoesNotExist:
        print(f"User with customer ID {customer_id} not found")
    except Exception as e:
        print(f"Error updating subscription: {str(e)}")

def handle_subscription_deleted(subscription):
    customer_id = subscription.get('customer')
    try:
        user = User.objects.get(stripe_customer_id=customer_id)
        user.cancel_subscription()
        print(f"Cancelled subscription for user {user.email}")
    except User.DoesNotExist:
        print(f"User with customer ID {customer_id} not found")
    except Exception as e:
        print(f"Error cancelling subscription: {str(e)}")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    user = request.user
    try:
        if not user.stripe_customer_id:
            return Response({"error": "No Stripe customer ID found."}, status=400)
        
        subscriptions = stripe.Subscription.list(
            customer=user.stripe_customer_id,
            status='active',
            limit=1
        )
        
        if not subscriptions.data:
            return Response({"error": "No active subscription found."}, status=400)
        
        subscription = subscriptions.data[0]
        
        updated_subscription = stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=True
        )
        
        cancel_at_ts = updated_subscription.cancel_at
        cancel_at_str = datetime.fromtimestamp(cancel_at_ts).strftime('%d/%m/%Y') if cancel_at_ts else None

        # Optional: store the cancel date locally
        # user.subscription_cancel_at = timezone.datetime.fromtimestamp(updated_subscription.cancel_at)
        # user.save()

        return Response({
            "message": "Subscription will be canceled at the end of the billing period.",
            "cancel_at": cancel_at_str
        })
    except Exception as e:
        return Response({"error": f"Cancellation failed: {str(e)}"}, status=400)
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def cancel_subscription(request):
#     user = request.user
#     try:
#         if not user.stripe_customer_id:
#             return Response({"error": "No Stripe customer ID found."}, status=400)
        
#         subscriptions = stripe.Subscription.list(
#             customer=user.stripe_customer_id,
#             status='active',
#             limit=1
#         )
        
#         if not subscriptions.data:
#             return Response({"error": "No active subscription found."}, status=400)
        
#         subscription = subscriptions.data[0]
        
#         updated_subscription = stripe.Subscription.modify(
#             subscription.id,
#             cancel_at_period_end=True
#         )

#         # Optional: store the cancel date locally
#         # user.subscription_cancel_at = timezone.datetime.fromtimestamp(updated_subscription.cancel_at)
#         # user.save()

#         return Response({
#             "message": "Subscription will be canceled at the end of the billing period.",
#             "cancel_at": updated_subscription.cancel_at
#         })
#     except Exception as e:
#         return Response({"error": f"Cancellation failed: {str(e)}"}, status=400)


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
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_subscription_status(request):
    user = request.user

    try:
        if not user.stripe_customer_id:
            return Response({
                "is_subscribed": False,
                "subscription_type": None,
                "subscription_start": None,
                "subscription_end": None
            })

        stripe_subs = stripe.Subscription.list(
            customer=user.stripe_customer_id,
            status='active',
            limit=1
        )

        if not stripe_subs.get('data'):
            return Response({
                "is_subscribed": False,
                "subscription_type": None,
                "subscription_start": None,
                "subscription_end": None
            })

        subscription = stripe_subs['data'][0]

        # ✅ Corrected access to current_period_end
        current_period_end = subscription['items']['data'][0]['current_period_end']

        user.update_subscription({
            'customer_id': user.stripe_customer_id,
            'subscription_type': user.subscription_type,
            'start_date': user.subscription_start,
            'end_date': timezone.datetime.fromtimestamp(current_period_end),
            'is_active': True
        })

        return Response(user.get_subscription_status())

    except Exception as e:
        print("Error in get_subscription_status:", str(e))
        return Response({"error": str(e)}, status=400)

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_subscription_status(request):
#     user = request.user
#     try:
#         if not user.stripe_customer_id:
#             print("User has no stripe_customer_id")
#             return Response({
#                 "is_subscribed": False,
#                 "subscription_type": None,
#                 "subscription_start": None,
#                 "subscription_end": None
#             })
        
#         # Get the customer's subscriptions from Stripe
#         subscriptions = stripe.Subscription.list(
#             customer=user.stripe_customer_id,
#             status='active',
#             limit=1
#         )
        
#         print("Stripe API response:", subscriptions)
        
#         if not subscriptions.data:
#             print("No active subscriptions found in Stripe")
#             return Response({
#                 "is_subscribed": False,
#                 "subscription_type": None,
#                 "subscription_start": None,
#                 "subscription_end": None
#             })
        
#         subscription = subscriptions.data[0]
        
#         # Extract current_period_end from the subscription item
#         current_period_end = subscription.items.data[0].current_period_end
        
#         # Update user's subscription data if needed
#         user.update_subscription({
#             'customer_id': user.stripe_customer_id,
#             'subscription_type': user.subscription_type,
#             'start_date': user.subscription_start,
#             'end_date': timezone.datetime.fromtimestamp(current_period_end),
#             'is_active': True
#         })
        
#         print("User subscription data after update:", user.get_subscription_status())
        
#         return Response(user.get_subscription_status())
#     except Exception as e:
#         print("Error in get_subscription_status:", str(e))
#         return Response({"error": str(e)}, status=400)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def cancel_subscription(request):
#     user = request.user
#     try:
#         if not user.stripe_customer_id:
#             return Response({"error": "No active subscription found"}, status=400)
        
#         # Get the customer's active subscription
#         subscriptions = stripe.Subscription.list(
#             customer=user.stripe_customer_id,
#             status='active',
#             limit=1
#         )
        
#         if not subscriptions.data:
#             return Response({"error": "No active subscription found"}, status=400)
        
#         subscription = subscriptions.data[0]
        
#         # Cancel the subscription at period end
#         updated_subscription = stripe.Subscription.modify(
#             subscription.id,
#             cancel_at_period_end=True
#         )
        
#         return Response({
#             "message": "Subscription will be canceled at the end of the billing period",
#             "cancel_at": updated_subscription.cancel_at
#         })
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def reactivate_subscription(request):
#     user = request.user
#     try:
#         if not user.stripe_customer_id:
#             return Response({"error": "No subscription found"}, status=400)
        
#         # Get the customer's subscription
#         subscriptions = stripe.Subscription.list(
#             customer=user.stripe_customer_id,
#             status='active',
#             limit=1
#         )
        
#         if not subscriptions.data:
#             return Response({"error": "No active subscription found"}, status=400)
        
#         subscription = subscriptions.data[0]
        
#         # Reactivate the subscription
#         updated_subscription = stripe.Subscription.modify(
#             subscription.id,
#             cancel_at_period_end=False
#         )
        
#         return Response({
#             "message": "Subscription reactivated successfully",
#             "subscription": {
#                 "id": updated_subscription.id,
#                 "status": updated_subscription.status,
#                 "current_period_end": updated_subscription.current_period_end
#             }
#         })
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_subscription_history(request):
    user = request.user
    try:
        if not user.stripe_customer_id:
            return Response({"error": "No subscription history found"}, status=400)
        
        # Get all subscriptions for the customer
        subscriptions = stripe.Subscription.list(
            customer=user.stripe_customer_id,
            limit=10  # Limit to last 10 subscriptions
        )
        
        subscription_history = []
        for sub in subscriptions.data:
            subscription_history.append({
                "id": sub.id,
                "status": sub.status,
                "start_date": sub.start_date,
                "current_period_start": sub.current_period_start,
                "current_period_end": sub.current_period_end,
                "canceled_at": sub.canceled_at,
                "ended_at": sub.ended_at
            })
        
        return Response({
            "subscription_history": subscription_history
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)