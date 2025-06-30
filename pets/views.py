from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils.timezone import make_aware, now
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters import DateFilter

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from datetime import datetime
from decimal import Decimal, InvalidOperation
from math import radians, sin, cos, sqrt, atan2
import cloudinary.uploader
import json

from .models import Pet, PetSightingHistory, Poster
from .serializers import PetSerializer, PetSightingHistorySerializer, PosterSerializer
from notifications.models import PushSubscription
from notifications.utils import send_push_notification

User = get_user_model()

# Maximum number of pets allowed per user
MAX_PETS_PER_USER = 5


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points using the Haversine formula.
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
        
    Returns:
        float: Distance in kilometers
    """
    R = 6371.0  # Radius of the Earth in kilometers

    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Difference in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# ============================================================================
# FILTERS AND PAGINATION
# ============================================================================

class PetFilter(filters.FilterSet):
    """Filter set for pet queries."""
    status = filters.NumberFilter(field_name='status', lookup_expr='exact')
    species = filters.NumberFilter(field_name='species', lookup_expr='exact') 
    age = filters.NumberFilter(field_name='age', lookup_expr='exact')
    gender = filters.NumberFilter(field_name='gender', lookup_expr='exact')
    size = filters.NumberFilter(field_name='size', lookup_expr='exact')
    pattern = filters.NumberFilter(field_name='pattern', lookup_expr='exact')
    date = DateFilter(field_name='event_occurred_at', lookup_expr='gte')
    color = filters.NumberFilter(method='filter_by_color')
    search = filters.CharFilter(method='filter_by_search', label='Search')
    
    def filter_by_color(self, queryset, name, value):
        """Filter pets by either primary_color or secondary_color matching the selected color."""
        return queryset.filter(
            Q(primary_color=value) | Q(secondary_color=value)
        )
    
    def filter_by_search(self, queryset, name, value):
        """Split the search string into separate terms. Allow searching on name and notes."""
        terms = value.strip().split()
        for term in terms:
            queryset = queryset.filter(
                Q(notes__icontains=term) | Q(identifier__icontains=term)
            )
        return queryset
    
    class Meta:
        model = Pet
        fields = ['search', 'species', 'age', 'gender', 'size', 'status', 'pattern', 'date', 'color']


class PetPagination(PageNumberPagination):
    """Pagination configuration for pet listings."""
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class PetSightingPagination(PageNumberPagination):
    """Pagination configuration for pet sightings."""
    page_size = 3
    page_size_query_param = 'page_size'


# ============================================================================
# PET MANAGEMENT VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_pets(request):
    """Fetch all pets created by the logged-in user."""
    user = request.user
    pets = Pet.objects.filter(author=user)
    serializer = PetSerializer(pets, many=True)
    return Response(serializer.data)


class PetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing pet objects."""
    queryset = Pet.objects.all().order_by('-created_at')
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PetFilter
    pagination_class = PetPagination
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Filter out closed pets for public view."""
        return Pet.objects.filter(is_closed=False).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List pets with pagination."""
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create a new pet with validation and image upload."""
        user = self.request.user
        current_count = Pet.objects.filter(author=user).count()
        
        if current_count >= MAX_PETS_PER_USER:
            raise ValidationError(
                f"You have reached the limit of {MAX_PETS_PER_USER} pets per user. Contact us if you need more."
            )

        uploaded_images = {}
        uploaded_images_list = []

        # Handle image uploads (at least one required)
        for i in range(1, 5):
            image_field = f"pet_image_{i}_media"
            image = self.request.FILES.get(image_field)

            if image:
                uploaded_image = cloudinary.uploader.upload(image)
                uploaded_images_list.append(uploaded_image.get("secure_url"))

        # Ensure at least one image is uploaded
        if not uploaded_images_list:
            raise ValidationError({"error": "At least one image must be uploaded."})

        # Assign images sequentially to pet_image_1, pet_image_2, etc.
        for index, image_url in enumerate(uploaded_images_list):
            uploaded_images[f"pet_image_{index+1}"] = image_url

        # Fill remaining image fields with None
        for i in range(len(uploaded_images_list) + 1, 5):
            uploaded_images[f"pet_image_{i}"] = None

        # Get date and time from request
        date = self.request.data.get("date")
        time = self.request.data.get("time")

        if date and time:
            try:
                combined_datetime_str = f"{date} {time}"
                event_occurred_at = datetime.strptime(combined_datetime_str, "%Y-%m-%d %H:%M")
                event_occurred_at = make_aware(event_occurred_at)
            except ValueError:
                event_occurred_at = now()
        else:
            event_occurred_at = now()

        pet = serializer.save(
            author=self.request.user,
            event_occurred_at=event_occurred_at,
            **uploaded_images
        )
        
        # Send notification if status is 'lost'
        if pet.status == 1:
            self.send_notifications_for_lost_pet(pet.id)

    def retrieve(self, request, pk=None):
        """Retrieve a specific pet."""
        pet = get_object_or_404(Pet, pk=pk)
        serializer = self.get_serializer(pet)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Update a pet (only by the author)."""
        pet = get_object_or_404(Pet, pk=pk, author=request.user)
        serializer = self.get_serializer(pet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """Delete a pet (only by the author)."""
        pet = get_object_or_404(Pet, pk=pk, author=request.user)
        pet.delete()
        return Response({"message": "Pet deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    def send_notifications_for_lost_pet(self, pet_id):
        """Send push notifications for lost pets to nearby users."""
        pet = Pet.objects.get(id=pet_id)
        subscriptions = PushSubscription.objects.all()
        nearby_users = []

        for subscription in subscriptions:
            distance = calculate_distance(
                pet.latitude, pet.longitude, 
                subscription.lat, subscription.lon
            )
            if distance <= subscription.distance:
                nearby_users.append(subscription)

        for subscription in nearby_users:
            image_url = pet.pet_image_1 if pet.pet_image_1 else "https://example.com/default-image.jpg"
            payload = {
                "title": f"Uzmanību! Netālu no jums ir {pet.get_status_display()} mājdzīvnieks!",
                "body": f"Netālu no jūsu atrašanās vietas ir {pet.get_status_display()} {pet.get_species_display()}!",
                "url": f"{settings.DOMAIN_APP_URL}/pets/{pet.id}",
                "image": image_url
            }
            send_push_notification(subscription, payload)

        return JsonResponse({"status": "Notifications sent to nearby users."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pet_post_quota(request):
    """Get the user's pet posting quota information."""
    user = request.user
    current_count = Pet.objects.filter(author=user).count()
    remaining = max(MAX_PETS_PER_USER - current_count, 0)

    return Response({
        'limit': MAX_PETS_PER_USER,
        'used': current_count,
        'remaining': remaining
    })


# ============================================================================
# PET SIGHTING VIEWS
# ============================================================================

class PetSightingView(APIView):
    """Handles creating pet sighting entry (POST), listing pet sightings (GET), and deleting a sighting (DELETE)."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, id):
        """List paginated pet sightings for a specific pet."""
        pet = get_object_or_404(Pet, id=id)
        sightings = PetSightingHistory.objects.filter(pet=pet)
        serializer = PetSightingHistorySerializer(sightings, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        """Create a new pet sighting entry."""
        pet = get_object_or_404(Pet, id=id)

        # Block new sightings if the pet report is closed
        if pet.is_closed:
            return Response(
                {"error": "Cannot add sightings to a closed pet report."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle image upload
        uploaded_image_url = None
        image = request.FILES.get('pet_image_media')
        
        if image:
            uploaded_image = cloudinary.uploader.upload(image)
            uploaded_image_url = uploaded_image.get("secure_url")

        # Get date and time from request
        date = request.data.get("date")
        time = request.data.get("time")

        if date and time:
            try:
                combined_datetime_str = f"{date} {time}"
                event_occurred_at = datetime.strptime(combined_datetime_str, "%Y-%m-%d %H:%M")
                event_occurred_at = make_aware(event_occurred_at)
            except ValueError:
                event_occurred_at = now()
        else:
            event_occurred_at = now()

        # Create sighting
        sighting_data = {
            'pet': pet,
            'status': request.data.get('status', 2),
            'latitude': request.data.get('latitude'),
            'longitude': request.data.get('longitude'),
            'notes': request.data.get('notes', ''),
            'reporter': request.user,
            'pet_image': uploaded_image_url,
            'is_public': request.data.get('is_public', True),
            'is_verified': False
        }

        sighting = PetSightingHistory.objects.create(**sighting_data)
        serializer = PetSightingHistorySerializer(sighting)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id, sighting_id):
        """Delete a specific pet sighting (only by the reporter)."""
        pet = get_object_or_404(Pet, id=id)
        sighting = get_object_or_404(PetSightingHistory, id=sighting_id, pet=pet)
        
        # Check if user is the reporter or pet owner
        if sighting.reporter != request.user and pet.author != request.user:
            return Response(
                {"error": "You don't have permission to delete this sighting."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        sighting.delete()
        return Response({"message": "Sighting deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# POSTER MANAGEMENT VIEWS
# ============================================================================

class UserPostersAPIView(APIView):
    """View for managing user posters."""
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """Get all posters for pets owned by the user."""
        user = request.user
        posters = Poster.objects.filter(pet__author=user)
        serializer = PosterSerializer(posters, many=True)
        return Response(serializer.data)


class PosterBulkCreateView(APIView):
    """View for creating multiple posters at once."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def post(self, request):
        """Create multiple posters for a pet."""
        pet_id = request.data.get('pet')
        name = request.data.get('name', '')
        count = int(request.data.get('count', 1))

        posters = []
        for i in range(count):
            poster_name = f"{name} #{i+1}" if count > 1 else name
            poster = Poster.objects.create(
                pet_id=pet_id,
                name=poster_name
            )
            posters.append({
                "id": str(poster.id),
                "pet": pet_id,
                "name": poster.name
            })
        
        return Response(posters, status=status.HTTP_201_CREATED)


class PosterDetailView(generics.RetrieveAPIView):
    """View for retrieving poster details."""
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    lookup_field = 'id'


@csrf_exempt
def increment_poster_scan(request, poster_id):
    """Increment the scan count for a poster."""
    if request.method == 'POST':
        data = json.loads(request.body or "{}")

        try:
            poster = Poster.objects.get(id=poster_id)
        except Poster.DoesNotExist:
            return JsonResponse({"error": "Poster not found."}, status=404)

        if not poster.has_location and data.get("latitude") and data.get("longitude"):
            poster.latitude = data["latitude"]
            poster.longitude = data["longitude"]
            poster.has_location = True

        poster.scans += 1
        poster.save()

        return JsonResponse({
            "status": "ok",
            "scans": poster.scans,
            "pet_id": poster.pet_id
        })


# ============================================================================
# STATISTICS AND ANALYTICS VIEWS
# ============================================================================

class PetStatusCountsView(APIView):
    """View for getting pet status statistics."""
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        """Get counts of pets by status."""
        status_counts = {}
        for status_choice in Pet.STATUS_CHOICES:
            status_counts[status_choice[1]] = Pet.objects.filter(status=status_choice[0]).count()
        
        return Response(status_counts)


class RecentPetsView(APIView):
    """View for getting recent pets."""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Get the most recent pets."""
        recent_pets = Pet.objects.filter(is_closed=False).order_by('-created_at')[:6]
        serializer = PetSerializer(recent_pets, many=True)
        return Response(serializer.data)