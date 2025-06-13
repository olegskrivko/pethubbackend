from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PushSubscription
from .serializers import PushSubscriptionSerializer
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import PushSubscription
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import PushSubscription
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import requests
import logging
from pywebpush import webpush, WebPushException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

vapid_private_key = settings.WEBPUSH_SETTINGS.get("VAPID_PRIVATE_KEY")


logger = logging.getLogger(__name__)

VAPID_PRIVATE_KEY = f"{vapid_private_key}"


from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import PushSubscription
from .serializers import PushSubscriptionSerializer

class PushSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = PushSubscription.objects.all()
    serializer_class = PushSubscriptionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow public read access, but auth required for write operations

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def subscribe(self, request):
        """
        Handle the subscription logic (saving or updating the subscription).
        """
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        subscription_data = request.data
        endpoint = subscription_data.get('endpoint')
        p256dh = subscription_data.get('p256dh')
        auth = subscription_data.get('auth')
        lat = subscription_data.get('lat', 56.946)
        lon = subscription_data.get('lon', 24.1059)
        distance = subscription_data.get('distance', 200.0)

        if not endpoint or not p256dh or not auth:
            return Response({"error": "Missing subscription data."}, status=status.HTTP_400_BAD_REQUEST)

        # Use update_or_create to handle existing devices
        subscription, created = PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={
                'p256dh': p256dh,
                'auth': auth,
                'lat': lat,
                'lon': lon,
                'distance': distance,
            }
        )

        return Response(
            {"message": "Subscription saved!" if created else "Subscription updated."},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    



    # Custom action for unsubscribing (removes the subscription from the database)
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def unsubscribe(self, request):
        """
        Handle the unsubscription logic (removing the subscription).
        """
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        subscription_data = request.data
        try:
            subscription = PushSubscription.objects.get(endpoint=subscription_data['endpoint'], user=request.user)
            subscription.delete()
            return Response({"message": "Unsubscribed successfully!"}, status=status.HTTP_200_OK)
        except PushSubscription.DoesNotExist:
            return Response({"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)

    # Send notifications (can be a separate view or action, depending on your use case)
    # @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])

    # def send_notification(self, request):
    #     @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def send_notification(self, request):
        # """
        # Send notifications to the subscribed users.
        # """
        # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            # Retrieve notification data
            data = request.data
            title = data.get('title')
            body = data.get('body')
            url = data.get('url')

            # Ensure title and body are provided
            if not all([title, body]):
                return Response({"error": "Missing required fields: title and body"}, status=status.HTTP_400_BAD_REQUEST)

            # Get all subscriptions for the user
            subscriptions = PushSubscription.objects.filter(user=request.user)
            if not subscriptions:
                return Response({"error": "No subscriptions found for this user"}, status=status.HTTP_404_NOT_FOUND)

            # Create notification payload
            payload = json.dumps({
                "title": title,
                "body": body,
                "url": url
            })

            failures = []

            # Loop through each subscription and send the push notification
            for subscription in subscriptions:
                try:
                    logger.info(f"Sending push notification to {subscription.endpoint}")
                    
                    # Sending the push notification via webpush
                    webpush(
                        subscription_info={
                            "endpoint": subscription.endpoint,
                            "keys": {
                                "p256dh": subscription.p256dh,
                                "auth": subscription.auth
                            }
                        },
                        data=payload,
                        vapid_private_key=settings.WEBPUSH_SETTINGS['VAPID_PRIVATE_KEY'],
                        # vapid_claims=settings.WEBPUSH_SETTINGS['VAPID_ADMIN_EMAIL']
                        vapid_claims={
        "sub": f"mailto:{settings.WEBPUSH_SETTINGS['VAPID_ADMIN_EMAIL']}"
    }
                    )
                except WebPushException as ex:
                    logger.error(f"Push failed for endpoint {subscription.endpoint}: {str(ex)}")
                    failures.append(subscription.endpoint)

            if failures:
                return Response({
                    "error": "Some notifications failed.",
                    "failed_endpoints": failures
                }, status=status.HTTP_207_MULTI_STATUS)

            return Response({"message": "Notification sent successfully!"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def is_subscribed(self, request):
        """
        Check if the current user is subscribed (optionally filtered by endpoint).
        """
        endpoint = request.query_params.get("endpoint")
        print("endpoint", endpoint)
        if not endpoint:
            return Response({"error": "Missing 'endpoint' query param."}, status=status.HTTP_400_BAD_REQUEST)

        exists = PushSubscription.objects.filter(user=request.user, endpoint=endpoint).exists()
        print("exists", exists)
        return Response({"subscribed": exists}, status=status.HTTP_200_OK)
    


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='user-location')
    def user_location(self, request):
        user = request.user

        # Get the latest PushSubscription for the user (by created_at, or any other logic)
        subscription = (
            PushSubscription.objects.filter(user=user)
            .order_by('-created_at')  # Or use .last() if you prefer
            .first()
        )

        if subscription:
            data = {
                'lat': subscription.lat,
                'lon': subscription.lon,
                'distance': subscription.distance,
            }
        else:
            # Fallback if user has no subscriptions
            data = {
                'lat': 56.946285,
                'lon': 24.105078,
                'distance': 5.0,
            }

        return Response(data, status=status.HTTP_200_OK)
    
    # Add this inside PushSubscriptionViewSet
    # @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    # def user_location(self, request):
    #     """
    #     Return the most recent PushSubscription's location for the current user.
    #     """
    #     subscription = (
    #         PushSubscription.objects
    #         .filter(user=request.user)
    #         .order_by('-created_at')
    #         .first()
    #     )

    #     if not subscription:
    #         return Response({"error": "No subscription found."}, status=404)

    #     return Response({
    #         "lat": subscription.lat,
    #         "lon": subscription.lon,
    #         "distance": subscription.distance,
    #         "endpoint": subscription.endpoint
    #     })
    

        # Custom action for subscribing (this is already handled by DRF's ModelViewSet `create` method)
    # @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    # def subscribe(self, request):
    #     """
    #     Handle the subscription logic (saving the subscription).
    #     """
    #     if not request.user.is_authenticated:
    #         return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    #     subscription_data = request.data
    #     subscription = PushSubscription(
    #         user=request.user,
    #         endpoint=subscription_data['endpoint'],
    #         p256dh=subscription_data['p256dh'],
    #         auth=subscription_data['auth']
    #     )
    #     subscription.save()
    #     return Response({"message": "Subscription saved!"}, status=status.HTTP_201_CREATED)