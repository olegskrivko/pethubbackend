# services/views.py
from rest_framework import serializers
from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend

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

User = get_user_model()

from django.shortcuts import render
from rest_framework.permissions import AllowAny

#Create your views here.
from rest_framework import viewsets
from .models import Shelter
from .serializers import ShelterSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters import rest_framework as filters


import django_filters

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Shelter
from .serializers import ShelterSerializer
from django_filters import rest_framework as filters
from django.db.models import Q


class ShelterPagination(PageNumberPagination):
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

class ShelterFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category', lookup_expr='exact')
    search = filters.CharFilter(method='filter_by_search', label='Search')

    def filter_by_search(self, queryset, name, value):
        """Split the search string into separate terms. Allow searching on title and description"""
        terms = value.strip().split()
        for term in terms:
            queryset = queryset.filter(
                Q(description__icontains=term) | Q(name__icontains=term)
            )
        return queryset

    class Meta:
        model = Shelter
        fields = ['search', 'category']



class ShelterViewSet(viewsets.ModelViewSet):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ShelterFilter
    pagination_class = ShelterPagination
    # parser_classes = (MultiPartParser, FormParser)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # def create(self, request, *args, **kwargs):
    #     print("Received request data:", request.data)

        # Step 1: Handle and extract location string → Python list
        # raw_locations = request.data.get("locations")
        # if isinstance(raw_locations, list):
        #     raw_locations = raw_locations[0]  # because QueryDict stores it as list
        # try:
        #     parsed_locations = json.loads(raw_locations) if raw_locations else []
        # except json.JSONDecodeError:
        #     raise ValidationError({"locations": "Invalid JSON format for locations."})

        # Step 2: Copy request data and manually inject parsed locations
    #     mutable_data = request.data.copy()
    #     mutable_data.setlist("locations", [])  # wipe it to avoid confusion
    #     serializer = self.get_serializer(data=mutable_data)
    #     serializer.is_valid(raise_exception=True)

    #     # Step 3: save and pass locations + images to perform_create
    #     self.perform_create(serializer, parsed_locations)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def perform_create(self, serializer, locations_data):
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


# @api_view(['GET'])
# @permission_classes([IsAuthenticatedOrReadOnly])
# def shelter_list(request):
#     shelters = Shelter.objects.all()
    
#     serializer = ShelterSerializer(shelters, many=True)
#     return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def shelter_detail(request, pk):
    shelter = Shelter.objects.get(pk=pk)
    serializer = ShelterSerializer(shelter)
    return Response(serializer.data)
# from rest_framework import viewsets
# from rest_framework.permissions import AllowAny
# from .models import Shelter
# from .serializers import ShelterSerializer

# class ShelterViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Shelter.objects.all()
#     serializer_class = ShelterSerializer

#     def get_permissions(self):
#         # Forcefully override global IsAuthenticated
#         return [AllowAny()]
