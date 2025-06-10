from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey to User to associate subscriptions with users
    endpoint = models.URLField()  # URL endpoint for the subscription
    p256dh = models.CharField(max_length=255)  # Encryption key for push subscription
    auth = models.CharField(max_length=255)  # Authentication key for push subscription
    # lat = models.FloatField()  # User's latitude for notification radius
    # lon = models.FloatField()  # User's longitude for notification radius
    lat = models.FloatField(default=56.946)  # Default latitude set to Riga
    lon = models.FloatField(default=24.1059)  # Default longitude set to Riga
    distance = models.FloatField(default=5.0)  # Default radius of 5 km
    created_at = models.DateTimeField(default=timezone.now)  # Track when the subscription was created

    def __str__(self):
        return f"Subscription for {self.user.username} at {self.lat}, {self.lon} within {self.distance} km"
        # return f"{self.user.username}'s subscription to {self.endpoint}"

    class Meta:
        unique_together = ('user', 'endpoint')  # Ensure a user can have only one subscription per endpoint
