# pets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetViewSet, PetSightingView,  RecentPetsView,PosterBulkCreateView, PetStatusCountsView, PosterDetailView,  get_user_pets, pet_post_quota  # get_pet_status_counts   # Import get_user_pets, PetSightingCreate, PetSightingHistoryViewSet,
from . import views

router = DefaultRouter()
router.register(r'', PetViewSet)
# router.register(r'pet-sightings', PetSightingView, basename='pet-sightings')  # Pet sightings viewset

urlpatterns = [
  
    # Place this route first to avoid it being matched as an ID
    #path('user-pets/', get_user_pets, name='get_user_pets'),  # Fetch pets for the logged-in user
    # path('status-counts/', get_pet_status_counts, name='pet-status-counts'),
    path('status-counts/', PetStatusCountsView.as_view(), name='pet-status-counts'),
    path('pet-quota/', pet_post_quota, name='pet-post-quota'),
    path('', include(router.urls)),  # Register PetViewSet in the API
    
    #path('<int:id>/pet-sightings/', PetSightingCreate.as_view(), name='create_pet_sighting'),  # New route for pet sightings
    path('<int:id>/pet-sightings/', PetSightingView.as_view(), name='pet_sightings'),
   # path('pet-sightings/<int:id>/', PetSightingView.as_view(), name='delete_pet_sighting'),  # DELETE route for a specific pet sighting
    path('<int:id>/pet-sightings/<int:sighting_id>/', PetSightingView.as_view(), name='delete_pet_sighting'),
    #path('pet-sightings/<int:pk>/', PetSightingHistoryViewSet.as_view({'delete': 'destroy'}), name='delete_pet_sighting'),  # DELETE pet sighting
    # path('<int:pk>/', PetViewSet.as_view({'put': 'update', 'patch': 'update'}), name='pet-update'),
    path('recent-pets/', RecentPetsView.as_view(), name='recent-pets'),
    #path('posters/', PosterCreateView.as_view(), name='poster-create'),
    path('posters/<uuid:id>/', PosterDetailView.as_view(), name='poster-detail'),
    # Your frontend generates several QR codes at once
    path('posters/bulk-create/', PosterBulkCreateView.as_view(), name='poster-bulk-create'),
    # path('posters/<uuid:poster_id>/set-location/', views.set_poster_location, name='set-poster-location'),
    # This is your scan endpoint used when people scan the QR code.
    path('posters/<uuid:poster_id>/scan/', views.increment_poster_scan, name='poster-scan'),
    #path('posters/<uuid:poster_id>/update-location/', views.update_poster_location, name='update-poster-location'),


] 

# path('', include(router.urls))
# Registers all default REST API routes for the PetViewSet using Django REST framework's router.
# router.urls automatically generates the list, create, retrieve, update, and delete endpoints.
# It follows RESTful conventions and is recommended for simple CRUD APIs.
# HTTP Method	URL	Action in ViewSet	Description
# GET	/api/pets/	list	Get all pets
# POST	/api/pets/	create	Add a new pet
# GET	/api/pets/1/	retrieve	Get details of pet with ID=1
# PUT	/api/pets/1/	update	Update pet with ID=1
# DELETE	/api/pets/1/	destroy	Delete pet with ID=1