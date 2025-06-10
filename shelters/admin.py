from django.contrib import admin
from .models import Shelter
# Register your models here.
@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'street', 'postal_code', 'latitude', 'longitude')
    list_filter = ('country', 'region', 'city')
    search_fields = ('name', 'city', 'street', 'postal_code')

