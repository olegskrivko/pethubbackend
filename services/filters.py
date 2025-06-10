
import django_filters
from .models import Service

class ServiceFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category")

    class Meta:
        model = Service
        fields = ['category']
