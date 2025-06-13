# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import PushSubscriptionViewSet

# # Create a router and register the PushSubscriptionViewSet
# router = DefaultRouter()
# router.register(r'', PushSubscriptionViewSet, basename='push-subscription')

# urlpatterns = [
#     path('', include(router.urls)),  # This will automatically generate the routes for subscribe, unsubscribe, and send_notification
#     path('user-location/', user_location, name='user-location'),  # Add this line
# ]
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import PushSubscriptionViewSet

# router = DefaultRouter()
# router.register(r'', PushSubscriptionViewSet, basename='push-subscription')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('user-location/', user_location, name='user-location'),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PushSubscriptionViewSet  # ✅ no user_location import

router = DefaultRouter()
router.register(r'', PushSubscriptionViewSet, basename='push-subscription')

urlpatterns = [
    path('', include(router.urls)),  # ✅ this includes /user-location/ because of @action
]
