# # Import the `path` and `include` functions for defining URL patterns
# from django.urls import path, include

# # Import DRF's router which automatically generates URL routes for ViewSets
# from rest_framework.routers import DefaultRouter

# # Import the ShelterViewSet which handles listing and retrieving shelters
# from .views import ShelterViewSet

# # Create a DRF router instance to auto-generate RESTful routes
# router = DefaultRouter()

# # Register the ShelterViewSet with the router
# # This will automatically create the following endpoints:
# # - GET /shelters/          → List all shelters
# # - GET /shelters/{id}/     → Retrieve a specific shelter by ID
# router.register(r'', ShelterViewSet, basename='shelter')

# # Define the URL patterns for this app
# urlpatterns = [
#     # Include all URLs generated by the router (i.e., /shelters/ endpoints)
#     path('', include(router.urls)),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shelters.views import  shelter_detail #shelter_list

from .views import ShelterViewSet

router = DefaultRouter()
router.register(r'', ShelterViewSet)
urlpatterns = [
    path('', include(router.urls)),
    # path('', shelter_list, name='shelter-list'),
    path('<int:pk>/', shelter_detail, name='shelter-detail'),
]

