# pets/serializers.py
#from django.contrib.auth.models import User 
from rest_framework import serializers
from .models import Pet, PetSightingHistory
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Include fields you want to display

class PetSightingHistorySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display')
    status = serializers.IntegerField()  # This ensures you return the raw integer value, not the display string
    reporter = UserSerializer(read_only=True)  # Serialize the User field
    #reporter = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)  # Make reporter writable (User ID)
    #image = serializers.ImageField(required=False, allow_null=True)  # Handle image field (optional)  # Handle image field (optional)
    #image_url = serializers.SerializerMethodField()  # ✅ Fix: Use `SerializerMethodField`
    pet_image = serializers.CharField(required=False, allow_blank=True)  # ✅ Accepts empty values
    pet = serializers.PrimaryKeyRelatedField(queryset=Pet.objects.all())  # ✅ Ensure `pet` exists
    #event_occurred_at = serializers.DateTimeField(required=False, allow_null=True)  # ✅ Ensure it's an aware datetime
    class Meta:
        model = PetSightingHistory
        fields = '__all__' 
        #fields = ['latitude', 'longitude', 'created_at', 'timestamp', 'reporter', 'notes', 'status', 'image', 'event_occurred_at']  # Add the fields you want to include

    # def get_image_url(self, obj):
    #     print("self",self)
    #     """ ✅ Return Cloudinary Image URL for sightings """
    #     return obj.image if obj.image else None

    # def validate(self, data):
    #     latitude = data.get('latitude')
    #     longitude = data.get('longitude')
    #     pet_image = data.get('pet_image')
    #     notes = data.get('notes')

    #     # If latitude or longitude is missing, require pet_image or notes
    #     if latitude is None or longitude is None:
    #         if not pet_image and not notes:
    #             raise serializers.ValidationError(
    #                 "Either coordinates, an image, or notes must be provided."
    #             )
    #     else:
    #         # Validate latitude and longitude ranges
    #         try:
    #             lat = float(latitude)
    #             lon = float(longitude)
    #         except (TypeError, ValueError):
    #             raise serializers.ValidationError("Latitude and longitude must be valid numbers.")

    #         if not (-90 <= lat <= 90):
    #             raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
    #         if not (-180 <= lon <= 180):
    #             raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")

    #     return data

    # def validate(self, data):
    #     # Check if latitude and longitude are provided and are valid
    #     """Ensure latitude and longitude are valid."""
    #     latitude = data.get('latitude')
    #     longitude = data.get('longitude')

    #     if not latitude or not longitude:
    #         raise serializers.ValidationError("Latitude and longitude must be provided.")
        
    #     try:
    #         latitude = float(latitude)
    #         longitude = float(longitude)
    #     except ValueError:
    #         raise serializers.ValidationError("Latitude and longitude must be valid numbers.")

    #     # Optionally, check for valid ranges
    #     if not (-90 <= latitude <= 90):
    #         raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
    #     if not (-180 <= longitude <= 180):
    #         raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        
    #     return data


class PetSerializer(serializers.ModelSerializer):
    print("i am in PetSerializer")
    size_display = serializers.CharField(source='get_size_display', read_only=True)
    contact_phone_display = serializers.CharField(source='get_contact_phone_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    species_display = serializers.CharField(source='get_species_display', read_only=True)
    behavior_display = serializers.CharField(source='get_behavior_display', read_only=True)
    age_display = serializers.CharField(source='get_age_display', read_only=True)
    pattern_display = serializers.CharField(source='get_pattern_display', read_only=True)
    primary_color_display = serializers.CharField(source='get_primary_color_display', read_only=True)
    secondary_color_display = serializers.CharField(source='get_secondary_color_display', read_only=True)

    pattern = serializers.IntegerField(required=False)
    primary_color = serializers.IntegerField(required=False)
    secondary_color = serializers.IntegerField(required=False)

    notes_display = serializers.CharField(source='get_notes_display', read_only=True)
    pet_image_1 = serializers.URLField(required=False, allow_blank=True)
    pet_image_2 = serializers.URLField(required=False, allow_blank=True)
    pet_image_3 = serializers.URLField(required=False, allow_blank=True)
    pet_image_4 = serializers.URLField(required=False, allow_blank=True)

    #event_occurred_at = serializers.DateTimeField(source='get_event_occurred_at_display', read_only=True)
    author = UserSerializer(read_only=True)  # Add the UserSerializer here
    
    # lets make api request for comments
    # sightings_history = PetSightingHistorySerializer(many=True, read_only=True)  # Include related sighting history

    #status_history = PetSightingHistorySerializer(many=True, read_only=True)
     # ✅ Accept `latitude`, `longitude`, and `status` as writeable fields (for the first sighting)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    # event_occurred_at = serializers.DateTimeField(required=True) 
    status = serializers.IntegerField(required=True)
     # This will return the human-readable value for the status
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    final_status = serializers.IntegerField(required=True)
    final_status_display = serializers.CharField(source='get_final_status_display', read_only=True)
    
    class Meta:
        model = Pet
        #fields = ['id', 'name']
        fields = '__all__'  # Include all fields from the model

    
        

    def create(self, validated_data):
        print("🔥 PetSerializer.create() hit!")  # Debugging Line
        pet = Pet.objects.create(**validated_data)
        print(f"✅ Pet {pet.id} saved successfully!")  # Debugging
        return pet

