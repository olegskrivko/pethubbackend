import django_filters
from .models import Shelter

class ShelterFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category")

    class Meta:
        model = Shelter
        fields = ['category']
