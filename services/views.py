
# services/views.py
from rest_framework import serializers
from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Service,  Review #WorkingHour, Location,
from .serializers import ServiceSerializer, ReviewSerializer
import cloudinary.uploader
from rest_framework import status

# from .filters import ServiceFilter
# Add this at the top if you haven't already
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as filters


import django_filters
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
import json
from .models import Service, Location
User = get_user_model()

class ServicePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'totalPages': self.page.paginator.num_pages,
            'currentPage': self.page.number,
            'results': data
        })

class ServiceFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category', lookup_expr='exact')
    search = filters.CharFilter(method='filter_by_search', label='Search')

    def filter_by_search(self, queryset, name, value):
        """Split the search string into separate terms. Allow searching on title and description"""
        terms = value.strip().split()
        for term in terms:
            queryset = queryset.filter(
                Q(description__icontains=term) | Q(title__icontains=term)
            )
        return queryset

    class Meta:
        model = Service
        fields = ['search', 'category']

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-created_at')
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ServiceFilter
    pagination_class = ServicePagination
    parser_classes = (MultiPartParser, FormParser)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        print("Received request data:", request.data)

        # Step 1: Handle and extract location string → Python list
        raw_locations = request.data.get("locations")
        if isinstance(raw_locations, list):
            raw_locations = raw_locations[0]  # because QueryDict stores it as list
        try:
            parsed_locations = json.loads(raw_locations) if raw_locations else []
        except json.JSONDecodeError:
            raise ValidationError({"locations": "Invalid JSON format for locations."})

        # Step 2: Copy request data and manually inject parsed locations
        mutable_data = request.data.copy()
        mutable_data.setlist("locations", [])  # wipe it to avoid confusion
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)

        # Step 3: save and pass locations + images to perform_create
        self.perform_create(serializer, parsed_locations)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, locations_data):
        print("hello from perform_create", locations_data)

        uploaded_images = {}
        uploaded_images_list = []

        for i in range(1, 5):
            image_field = f"service_image_{i}_media"
            image = self.request.FILES.get(image_field)
            if image:
                uploaded_image = cloudinary.uploader.upload(image)
                uploaded_images_list.append(uploaded_image.get("secure_url"))

        if not uploaded_images_list:
            raise ValidationError({"error": "At least one image must be uploaded."})

        for index, image_url in enumerate(uploaded_images_list):
            uploaded_images[f"service_image_{index+1}"] = image_url
        for i in range(len(uploaded_images_list) + 1, 5):
            uploaded_images[f"service_image_{i}"] = None

        service = serializer.save(user=self.request.user, **uploaded_images)

        # Create related location objects
            # Create related location objects with correct field mapping
        for loc in locations_data:
            if not all(k in loc for k in ("title", "description", "lat", "lng", "region", "city", "street", "postal_code", "full_address" )):
                raise ValidationError({"locations": "Each location must include title, description, lat, and lng."})
            
            try:
                lat = float(loc["lat"])
                lng = float(loc["lng"])
            except ValueError:
                raise ValidationError({"locations": "Latitude and Longitude must be valid numbers."})

            Location.objects.create(
                service=service,
                location_title=loc["title"],
                location_description=loc["description"],
                latitude=lat,
                longitude=lng,
                region=loc["region"],
                city=loc["city"],
                street=loc["street"],
                postal_code=loc["postal_code"],
                full_address=loc["full_address"],
            )
        # for loc in locations_data:
        #     if not all(k in loc for k in ("title", "description", "lat", "lng")):
        #         raise ValidationError({"locations": "Each location must include title, description, lat, and lng."})
        #     Location.objects.create(service=service, **loc)

# class ServiceViewSet(viewsets.ModelViewSet):
#     queryset = Service.objects.all().order_by('-created_at')  # Order by created_at in descending order
#     serializer_class = ServiceSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]  # Allow public read access, but auth required for write operations
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_class = ServiceFilter
#     pagination_class = ServicePagination
#     parser_classes = (MultiPartParser, FormParser)

#     # def get_queryset(self):
#     #     return super().get_queryset()

#     def list(self, request, *args, **kwargs):
#         # The pagination logic is handled automatically by the pagination class
#         return super().list(request, *args, **kwargs)

       
#     def perform_create(self, serializer):
#         uploaded_images = {}
#         uploaded_images_list = []  # Store uploaded images in order

#         # Handle image uploads (at least one required)
#         for i in range(1, 5):  # Loop from service_image_1 to service_image_4
#             image_field = f"service_image_{i}_media"  # Field name from request
#             image = self.request.FILES.get(image_field)

#             if image:
#                 uploaded_image = cloudinary.uploader.upload(image)
#                 uploaded_images_list.append(uploaded_image.get("secure_url"))

#         # Ensure at least one image is uploaded
#         if not uploaded_images_list:
#             raise ValidationError({"error": "At least one image must be uploaded."})

#             # Assign images sequentially to service_image_1, service_image_2, etc.
#         for index, image_url in enumerate(uploaded_images_list):
#             print("image_url", image_url)
#             uploaded_images[f"service_image_{index+1}"] = image_url  # Assign in order

#             # Fill remaining image fields with None
#         for i in range(len(uploaded_images_list) + 1, 5):  # Ensure all 4 fields exist
        
#             uploaded_images[f"service_image_{i}"] = None

#         serializer.save(user=self.request.user, **uploaded_images)

class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return Review.objects.filter(service_id=service_id)

    def perform_create(self, serializer):
        user = self.request.user
        service_id = self.kwargs['service_id']
        service = Service.objects.get(id=service_id)

        # Check if the review already exists
        existing_review = Review.objects.filter(user=user, service=service).first()

        if existing_review:
            # Update existing review with validated data
            existing_review.rating = serializer.validated_data['rating']
            existing_review.comment = serializer.validated_data['comment']
            existing_review.save()
        else:
            # Create a new review using serializer (which already has validated data)
            serializer.save(user=user, service=service)



