from rest_framework import serializers
from .models import PushSubscription
from rest_framework.reverse import reverse

class PushSubscriptionSerializer(serializers.ModelSerializer):
    unsubscribe_url = serializers.SerializerMethodField()

    class Meta:
        model = PushSubscription
        fields = ['id', 'user', 'endpoint', 'p256dh', 'auth', 'created_at', 'unsubscribe_url', 'lat', 'lon', 'distance']

    def get_unsubscribe_url(self, obj):
        """
        Generate a URL for unsubscribing the user from notifications.
        """
        return reverse('unsubscribe', args=[obj.id], request=self.context.get('request'))

    def validate(self, attrs):
        """
        Ensure that 'auth' and 'p256dh' are provided and valid.
        """
        if not attrs.get('auth') or not attrs.get('p256dh'):
            raise serializers.ValidationError("Both 'auth' and 'p256dh' fields must be provided.")
        
        # Optionally, ensure that 'lat', 'lon' and 'distance' are valid as well
        if 'lat' not in attrs or 'lon' not in attrs:
            raise serializers.ValidationError("Latitude and Longitude must be provided.")
        
        if 'distance' in attrs and attrs['distance'] < 0:
            raise serializers.ValidationError("Distance must be a positive value.")

        return attrs
