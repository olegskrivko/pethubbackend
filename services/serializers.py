# services/serializers.py
from rest_framework import serializers
from .models import Service,  Review,  Location #, WorkingHour,SocialMedia,
import logging
import json
logger = logging.getLogger(__name__)
# class WorkingHourSerializer(serializers.ModelSerializer):
#     day_display = serializers.CharField(source='get_day_display')

#     class Meta:
#         model = WorkingHour
#         fields = '__all__' 
# correct was workign
# class LocationSerializer(serializers.ModelSerializer):
#     working_hours = WorkingHourSerializer(many=True, read_only=True)
#     latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
#     longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)

#     class Meta:
#         model = Location
#         fields = '__all__' 

# class LocationSerializer(serializers.ModelSerializer):
#     working_hours = WorkingHourSerializer(many=True)

#     class Meta:
#         model = Location
#         fields = '__all__'

#     def create(self, validated_data):
#         # Extract the nested working_hours data
#         working_hours_data = validated_data.pop('working_hours', [])
#         # Create the Location object
#         location = Location.objects.create(**validated_data)
#         # Create the working hours for the location
#         for wh_data in working_hours_data:
#             WorkingHour.objects.create(location=location, **wh_data)
#         return location
#     def create(self, validated_data):
#         working_hours_data = validated_data.pop('working_hours')
#         location = Location.objects.create(**validated_data)
#         for wh_data in working_hours_data:
#             WorkingHour.objects.create(location=location, **wh_data)
#         return location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        # extra_kwargs = {
        #     'service': {'required': False},  # Let the view set it
        # }

# class SocialMediaSerializer(serializers.ModelSerializer):
#     platform = serializers.CharField(source='get_platform_display', read_only=True)
#     class Meta:
#         model = SocialMedia
#         fields = ['id', 'platform', 'profile_url']  # Include 'id' for write operations

class ServiceSerializer(serializers.ModelSerializer):
    # locations = LocationSerializer(many=True, required=False)
    locations = LocationSerializer(many=True, read_only=True)  # only for display
    # locations = LocationSerializer(many=True)
    user = serializers.ReadOnlyField(source='user.username')  # Optional: Display username
    category_display = serializers.CharField(source='get_category_display', read_only=True)  # 👈 Add this
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    price_type_display = serializers.CharField(source='get_price_type_display', read_only=True)
    
    service_image_1 = serializers.URLField(required=False, allow_blank=True)
    service_image_2 = serializers.URLField(required=False, allow_blank=True)
    service_image_3 = serializers.URLField(required=False, allow_blank=True)
    service_image_4 = serializers.URLField(required=False, allow_blank=True)
    # social_media = SocialMediaSerializer(many=True, read_only=True)
    # Allow creating/updating social media via IDs
    # social_media = serializers.PrimaryKeyRelatedField(
    #     queryset=SocialMedia.objects.all(), many=True, required=False
    # )


    rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return round(obj.average_rating(), 1)  # Use the method defined in the model

    def get_review_count(self, obj):
        return obj.review_count()  # Call the review_count() method from the Service model

    class Meta:
        model = Service
        fields = '__all__' 
        
    # def validate(self, data):
    #     if not data.get('locations') and self.context['request'].method == 'POST':
    #         raise serializers.ValidationError({
    #             "locations": "At least one location is required when creating a service."
    #         })
    #     return data
    # def validate(self, data):
    #     request = self.context.get('request')
    #     logger.debug("Validating data in ServiceSerializer for %s: %s", request.method if request else "unknown", data)

    #     if not data.get('locations') and request and request.method == 'POST':
    #         raise serializers.ValidationError({
    #             "locations": "At least one location is required when creating a service."
    #         })
    #     return data
    def validate(self, data):
        request = self.context.get('request')
        print("validated data in serializer:", data)

        if request and request.method == 'POST':
            # We must check locations from the raw request because DRF won't parse nested JSON in multipart
            raw_locations = request.data.get('locations')
            if isinstance(raw_locations, list):
                raw_locations = raw_locations[0]

            try:
                parsed_locations = json.loads(raw_locations)
            except (TypeError, json.JSONDecodeError):
                parsed_locations = []

            if not parsed_locations:
                raise serializers.ValidationError({
                    "locations": "At least one location is required when creating a service."
                })

        return data




    # def create(self, validated_data):
    #     locations_data = validated_data.pop('locations', [])
    #     social_media_data = validated_data.pop('social_media', [])
        
    #     service = Service.objects.create(**validated_data)

    #     for loc_data in locations_data:
    #         Location.objects.create(service=service, **loc_data)

    #     if social_media_data:
    #         service.social_media.set(social_media_data)

    #     return service

    def create(self, validated_data):
        locations_data = validated_data.pop('locations', [])
        social_media_data = validated_data.pop('social_media', [])

        logger.debug("Creating service with validated_data: %s", validated_data)
        logger.debug("Locations data: %s", locations_data)
        logger.debug("Social media data: %s", social_media_data)

        try:
            service = Service.objects.create(**validated_data)
        except Exception as e:
            logger.exception("Error creating Service instance")
            raise serializers.ValidationError({"service_creation": str(e)})

        for loc_data in locations_data:
            try:
                Location.objects.create(service=service, **loc_data)
            except Exception as e:
                logger.exception("Error creating Location with data: %s", loc_data)
                raise serializers.ValidationError({"location_creation": str(e)})

        if social_media_data:
            try:
                service.social_media.set(social_media_data)
            except Exception as e:
                logger.exception("Error setting social media")
                raise serializers.ValidationError({"social_media": str(e)})

        return service

    def update(self, instance, validated_data):
        locations_data = validated_data.pop('locations', None)
        social_media_data = validated_data.pop('social_media', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if social_media_data is not None:
            instance.social_media.set(social_media_data)

        if locations_data is not None:
            # Remove old locations
            instance.locations.all().delete()
            for loc_data in locations_data:
                Location.objects.create(service=instance, **loc_data)

        return instance



    

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    def validate_rating(self, value):
        if value is None:
            raise serializers.ValidationError("Rating is required.")
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at', 'user_name', 'user', 'service']
        read_only_fields = ['id', 'created_at', 'user', 'service']


