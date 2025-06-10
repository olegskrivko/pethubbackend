from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PushSubscriptionViewSet

# Create a router and register the PushSubscriptionViewSet
router = DefaultRouter()
router.register(r'', PushSubscriptionViewSet, basename='push-subscription')

urlpatterns = [
    path('', include(router.urls)),  # This will automatically generate the routes for subscribe, unsubscribe, and send_notification
]
