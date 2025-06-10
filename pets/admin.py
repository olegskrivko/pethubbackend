from django.contrib import admin
from .models import Pet, PetSightingHistory, UserFavorites
# Register your models here.



admin.site.register(PetSightingHistory)
admin.site.register(UserFavorites)

@admin.register(Pet)
class ShelterAdmin(admin.ModelAdmin):
    # list_display = ('name', 'size', 'species', 'gender')
    list_display = ('size', 'species', 'gender')
    list_filter = ('species', 'gender')
    search_fields = ('species', 'gender', 'size')


