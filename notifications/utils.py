# notifications/utils.py
import json
from pywebpush import webpush, WebPushException
from django.conf import settings
import logging
# pets/utils.py
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance

logger = logging.getLogger(__name__)

def send_push_notification(subscription, payload):
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
            data=json.dumps(payload),  # Ensure payload is a valid JSON string
            vapid_private_key=settings.WEBPUSH_SETTINGS['VAPID_PRIVATE_KEY'],
            vapid_claims={"sub": f"mailto:{settings.WEBPUSH_SETTINGS['VAPID_ADMIN_EMAIL']}"}
        )
        logger.info(f"Notification sent to {subscription.endpoint}")

    except WebPushException as ex:
        logger.error(f"Push failed for endpoint {subscription.endpoint}: {str(ex)}")
        raise ex  # Raise again to be handled if necessary
