from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pet, PetSightingHistory
from .serializers import PetSerializer, PetSightingHistorySerializer
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
#from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from django.utils.timezone import make_aware
from datetime import datetime
from django.utils import timezone
import django_filters
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
# from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from decimal import Decimal
from django.utils.timezone import now
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters import DateFilter
# from .models import PushSubscription
from math import radians, sin, cos, sqrt, atan2
from django.http import JsonResponse
from django.conf import settings
from notifications.models import PushSubscription

from notifications.utils import send_push_notification  # Import the push notification function
def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

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

    # Distance in kilometers
    distance = R * c
    return distance
User = get_user_model()

class PetFilter(filters.FilterSet):
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
        """ Filter pets by either primary_color or secondary_color matching the selected color """
        return queryset.filter(
            Q(primary_color=value) | Q(secondary_color=value)
        )
    
    def filter_by_search(self, queryset, name, value):
        """Split the search string into separate terms. Allow searching on name and notes"""
        terms = value.strip().split()
        for term in terms:
            queryset = queryset.filter(
                Q(notes__icontains=term) | Q(identifier__icontains=term)
            )
        return queryset
    
    class Meta:
        model = Pet
        fields = ['search', 'species', 'age', 'gender', 'size', 'status', 'pattern', 'date', 'color']


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access
def get_user_pets(request):
    """
    Fetch all pets created by the logged-in user.
    """
    print(request)
    user = request.user  # Get the logged-in user
    print(request)
    pets = Pet.objects.filter(author=user)
    serializer = PetSerializer(pets, many=True)
    return Response(serializer.data)


class PetStatusCountsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        lost_count = Pet.objects.filter(status=1).count()
        found_count = Pet.objects.filter(status=2).count()
        seen_count = Pet.objects.filter(status=3).count()

        return Response({
            'lost': lost_count,
            'found': found_count,
            'seen': seen_count,
        })

class PetPagination(PageNumberPagination):
    page_size = 6  # Default page size
    page_size_query_param = 'page_size'  # Allow clients to set the page size
    max_page_size = 100  # Max number of items per page
    # You can override the `get_paginated_response` method if you want to customize the structure of the response.
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Total number of pets
            'totalPages': self.page.paginator.num_pages,  # Total pages
            'currentPage': self.page.number,  # Current page number
            'results': data  # The paginated results
        })

    
class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all().order_by('-created_at')  # Order by created_at in descending order (most recent first)
    serializer_class = PetSerializer
    
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow public read access, but auth required for write operations
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = PetFilter
    pagination_class = PetPagination
    # filterset_fields = {
    #     'species': ['in', 'exact'],  # Filter by species (multiple species allowed)
    #     'breed': ['exact'],          # You can filter by breed if needed
    #     'age': ['exact', 'gte', 'lte'],  # Filter by age (exact, greater than, or less than)
    # }
    parser_classes = (MultiPartParser, FormParser)
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Optional: you can still customize filtering behavior if needed here, but filterset_class should handle most cases
        return queryset


    
    def list(self, request, *args, **kwargs):
        # The pagination logic is handled automatically by the pagination class
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):

        uploaded_images = {}
        uploaded_images_list = []  # Store uploaded images in order

        # Handle image uploads (at least one required)
        for i in range(1, 5):  # Loop from pet_image_1 to pet_image_4
            image_field = f"pet_image_{i}_media"  # Field name from request
            image = self.request.FILES.get(image_field)

            if image:
                uploaded_image = cloudinary.uploader.upload(image)
                uploaded_images_list.append(uploaded_image.get("secure_url"))

        # Ensure at least one image is uploaded
        if not uploaded_images_list:
            raise ValidationError({"error": "At least one image must be uploaded."})

        # Assign images sequentially to pet_image_1, pet_image_2, etc.
        for index, image_url in enumerate(uploaded_images_list):
            uploaded_images[f"pet_image_{index+1}"] = image_url  # Assign in order

        # Fill remaining image fields with None
        for i in range(len(uploaded_images_list) + 1, 5):  # Ensure all 4 fields exist
            uploaded_images[f"pet_image_{i}"] = None
        # image_1 = self.request.FILES.get('pet_image_1_media')
        # image_2 = self.request.FILES.get('pet_image_2_media')
        # image_3 = self.request.FILES.get('pet_image_3_media')
        # image_4 = self.request.FILES.get('pet_image_4_media')
        # uploaded_image_1_url = None
        # uploaded_image_2_url = None
        # uploaded_image_3_url = None
        # uploaded_image_4_url = None
        # if image_1:
        #     uploaded_image_1 = cloudinary.uploader.upload(image_1)
        #     uploaded_image_1_url = uploaded_image_1.get("secure_url")
        # if image_2:
        #     uploaded_image_2 = cloudinary.uploader.upload(image_2)
        #     uploaded_image_2_url = uploaded_image_2.get("secure_url")
        # if image_3:
        #     uploaded_image_3 = cloudinary.uploader.upload(image_3)
        #     uploaded_image_3_url = uploaded_image_3.get("secure_url")
        # if image_4:
        #     uploaded_image_4 = cloudinary.uploader.upload(image_4)
        #     uploaded_image_4_url = uploaded_image_4.get("secure_url")

            # Get date and time from request
        date = self.request.data.get("date")  # e.g., "2025-04-01"
        time = self.request.data.get("time")  # e.g., "14:30"
        print("date", self.request.data.get("date"))

        if date and time:
            try:
                # Combine date and time into a single string
                combined_datetime_str = f"{date} {time}"
                # Parse the combined string into a datetime object
                event_occurred_at = datetime.strptime(combined_datetime_str, "%Y-%m-%d %H:%M")
                # Make it timezone-aware
                event_occurred_at = make_aware(event_occurred_at)
            except ValueError:
                event_occurred_at = timezone.now()  # Default to now if the date/time is invalid
        else:
            event_occurred_at = timezone.now()  # Default to now if missing

        pet = serializer.save(
            author=self.request.user,
            # pet_image_1=uploaded_image_1_url,
            # pet_image_2=uploaded_image_2_url,
            # pet_image_3=uploaded_image_3_url,
            # pet_image_4=uploaded_image_4_url,
            event_occurred_at=event_occurred_at,
             **uploaded_images  # Dynamically assign images
        )
        # Send notification if status is 'lost'
        if pet.status == 1:  # Or any other condition you want
            self.send_notifications_for_lost_pet(pet.id)

    def retrieve(self, request, pk=None):
        pet = get_object_or_404(Pet, pk=pk)
        serializer = self.get_serializer(pet)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        pet = get_object_or_404(Pet, pk=pk, author=request.user)
        serializer = self.get_serializer(pet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def destroy(self, request, pk=None):
        pet = get_object_or_404(Pet, pk=pk, author=request.user)
        pet.delete()
        return Response({"message": "Pet deleted successfully."}, status=204)
    
    def send_notifications_for_lost_pet(self, pet_id):
        pet = Pet.objects.get(id=pet_id)

        subscriptions = PushSubscription.objects.all()
        nearby_users = []

        for subscription in subscriptions:
            distance = calculate_distance(pet.latitude, pet.longitude, subscription.lat, subscription.lon)
            if distance <= subscription.distance:
                nearby_users.append(subscription)


        for subscription in nearby_users:
            # Check if the pet has an image URL in pet_image_1, otherwise use a default image
            image_url = pet.pet_image_1 if pet.pet_image_1 else "https://example.com/default-image.jpg"
            payload = {
                "title": f"Uzmanību! Netālu no jums ir {pet.get_status_display()} mājdzīvnieks!",
                "body": f"Netālu no jūsu atrašanās vietas ir {pet.get_status_display()} {pet.get_species_display()}!",
                "url": f"{settings.DOMAIN_APP_URL}/pets/{pet.id}",
                "image": image_url  # Add the image URL to the payload
            }
            send_push_notification(subscription, payload)

        return JsonResponse({"status": "Notifications sent to nearby users."})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def pet_post_quota(request):
#     user = request.user
#     pet_limit = 1  # default
#     if user.is_subscribed and user.subscription_type == 'plus':
#         pet_limit = 5
#     current_count = Pet.objects.filter(author=user).count()
#     return Response({
#         'limit': pet_limit,
#         'used': current_count,
#         'remaining': pet_limit - current_count
#     })
class PetSightingView(APIView):
    """Handles creating pet sighting entry (POST), listing pet sightings (GET), and deleting a sighting (DELETE)"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, id):
        # List pet sightings for a specific pet
        pet = get_object_or_404(Pet, id=id)
        sightings = PetSightingHistory.objects.filter(pet=pet)
        serializer = PetSightingHistorySerializer(sightings, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        # Create a new pet sighting entry
        pet = get_object_or_404(Pet, id=id)

        status_value = request.data.get('status')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        notes = request.data.get('notes', '')
        reporter = request.user

        # Validate `status`
        try:
            status_value = int(status_value)
            if status_value not in dict(PetSightingHistory.STATUS_CHOICES):
                return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid status format"}, status=status.HTTP_400_BAD_REQUEST)

        # Handle image upload (if provided)
        image_url = None
        image = request.FILES.get('image')
        if image:
            uploaded_image = cloudinary.uploader.upload(image)
            image_url = uploaded_image.get("secure_url")


        # Validate latitude/longitude only if provided
        if latitude is not None and longitude is not None:
            try:
                latitude = Decimal(latitude)
                longitude = Decimal(longitude)
                if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                    return Response({"error": "Latitude must be between -90 and 90 and longitude between -180 and 180."}, status=status.HTTP_400_BAD_REQUEST)
            except (InvalidOperation, ValueError):
                return Response({"error": "Invalid latitude or longitude format"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If no coordinates provided, require at least image or notes to be present
            if not image_url and not notes:
                return Response({"error": "Either coordinates, an image, or notes must be provided."}, status=status.HTTP_400_BAD_REQUEST)
        # Validate latitude/longitude
        # if latitude and longitude:
        #     try:
        #         latitude = Decimal(latitude)
        #         longitude = Decimal(longitude)
        #     except (InvalidOperation, ValueError):
        #         return Response({"error": "Invalid latitude or longitude format"}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({"error": "Latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the pet sighting in the database
        sighting = PetSightingHistory.objects.create(
            pet=pet,
            status=status_value,
            latitude=latitude if latitude is not None else None,
            longitude=longitude if longitude is not None else None,
            # event_occurred_at=event_occurred_at,
            notes=notes,
            reporter=reporter,
            pet_image=image_url
        )


        # Return success response
        return Response({
            "id": sighting.id,
            "pet": sighting.pet.id,
            "status": sighting.get_status_display(),
            "latitude": sighting.latitude,
            "longitude": sighting.longitude,
            # "event_occurred_at": sighting.event_occurred_at,
            "notes": sighting.notes,
            "image": sighting.pet_image,
            "reporter": sighting.reporter.id,
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, id, sighting_id):
        """
        Delete a pet sighting entry.
        Only the user who reported the sighting (sighting.reporter) can delete it.
        """
        # Get the pet instance by its ID
        pet = get_object_or_404(Pet, id=id)
        
        # Get the pet sighting instance by its ID and ensure it belongs to the pet
        sighting = get_object_or_404(PetSightingHistory, id=sighting_id, pet=pet)

        # Ensure that only the user who reported the sighting can delete it
        if sighting.reporter != request.user:
            raise PermissionDenied("You are not authorized to delete this sighting.")

        # Perform the deletion
        sighting.delete()

        return Response({"message": "Pet sighting deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    
class RecentPetsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Assuming you want the most recent pets based on some ordering criteria
            recent_pets = Pet.objects.all().order_by('-created_at')[:4]  # Adjust based on your criteria
            serializer = PetSerializer(recent_pets, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
