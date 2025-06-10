from rest_framework import serializers
from .models import Shelter, SocialMedia, AnimalType

class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = ['id', 'name']
class SocialMediaSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(source='get_platform_display', read_only=True)
    class Meta:
        model = SocialMedia
        fields = ['platform', 'profile_url']

class ShelterSerializer(serializers.ModelSerializer):
        # Serialize the social media names
    animal_types = AnimalTypeSerializer(many=True, read_only=True)
    social_media = SocialMediaSerializer(many=True, read_only=True)
    class Meta:
        model = Shelter
        fields =  '__all__'