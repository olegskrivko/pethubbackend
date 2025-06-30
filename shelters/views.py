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


# ============================================================================
# PAGINATION AND FILTERS
# ============================================================================

class ShelterPagination(PageNumberPagination):
    """Pagination configuration for shelter listings."""
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
    """Filter set for shelter queries."""
    category = filters.NumberFilter(field_name='category', lookup_expr='exact')
    search = filters.CharFilter(method='filter_by_search', label='Search')

    def filter_by_search(self, queryset, name, value):
        """Split the search string into separate terms. Allow searching on title and description."""
        terms = value.strip().split()
        for term in terms:
            queryset = queryset.filter(
                Q(description__icontains=term) | Q(name__icontains=term)
            )
        return queryset

    class Meta:
        model = Shelter
        fields = ['search', 'category']


# ============================================================================
# SHELTER MANAGEMENT VIEWS
# ============================================================================

class ShelterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shelter objects.
    Supports CRUD operations with filtering and pagination.
    """
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ShelterFilter
    pagination_class = ShelterPagination

    def list(self, request, *args, **kwargs):
        """List shelters with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def shelter_detail(request, pk):
    """Get detailed information about a specific shelter."""
    shelter = Shelter.objects.get(pk=pk)
    serializer = ShelterSerializer(shelter)
    return Response(serializer.data)
