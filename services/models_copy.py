# from django.db import models
# from django.contrib.auth import get_user_model
# from django.conf import settings
# from django.contrib.gis.db import models as geomodels

# User = get_user_model()

# class Region(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

# class Service(models.Model):
#     SERVICE_CATEGORIES = [
#         (1, 'Dzīvnieku pieskatīšana'),
#         (2, 'Suņu pastaigas'),
#         (3, 'Kopšana'),
#         (4, 'Apmācība'),
#         (5, 'Izmitināšana'),
#         (6, 'Veterinārārsts'),
#         (7, 'Foto sesijas'),
#         (8, 'Glābšana un meklēšana'),
#         (9, 'Piederumi un aksesuāri'),
#         (10, 'Māksla'),
#         (11, 'Apbedīšana'),
#         (12, 'Transports'),
#         (13, 'Audzētavas'),
#         (14, 'Apdrošināšana'),
#         (15, 'Citi pakalpojumi'),
#     ]

#     PROVIDER_TYPES = [
#         (1, 'Fiziska persona'),
#         (2, 'Juridiska persona'),
#     ]

#     PHONE_CODE_CHOICES = [
#         (371, 'LV (+371)'),
#         (370, 'LT (+370)'),
#         (372, 'EE (+372)'),
#     ]

#     PRICE_TYPE_CHOICES = [
#         (1, 'Stundā'),
#         (2, 'Vienībā'),
#         (3, 'Dienā'),
#         (4, 'Pēc vienošanās'),
#     ]

#     PET_TYPES = [
#         (1, 'Suns'),
#         (2, 'Kaķis'),
#         (3, 'Putns'),
#         (4, 'Grauzējs'),
#         (5, 'Eksotisks dzīvnieks'),
#         (6, 'Cits'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
#     title = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     price_type = models.IntegerField(choices=PRICE_TYPE_CHOICES, default=1)
#     category = models.IntegerField(choices=SERVICE_CATEGORIES)
#     provider_type = models.IntegerField(choices=PROVIDER_TYPES)
#     pet_type = models.IntegerField(choices=PET_TYPES, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#     is_available = models.BooleanField(default=True)
#     is_online = models.BooleanField(default=False)
#     service_image_1 = models.URLField(max_length=255)
#     service_image_2 = models.URLField(max_length=255, null=True, blank=True)
#     service_image_3 = models.URLField(max_length=255, null=True, blank=True)
#     service_image_4 = models.URLField(max_length=255, null=True, blank=True)
#     website = models.URLField(blank=True, null=True)
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     phone_code = models.CharField(max_length=5, null=True, blank=True, choices=PHONE_CODE_CHOICES)
#     email = models.EmailField(blank=True, null=True)
#     average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
#     review_count = models.PositiveIntegerField(default=0)
#     tags = models.CharField(max_length=255, blank=True)

#     def __str__(self):
#         return self.title

# class Review(models.Model):
#     service = models.ForeignKey(Service, related_name='reviews', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     rating = models.DecimalField(max_digits=2, decimal_places=1)
#     comment = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_approved = models.BooleanField(default=True)

#     class Meta:
#         unique_together = ('service', 'user')

# class Location(models.Model):
#     service = models.ForeignKey(Service, related_name='locations', on_delete=models.CASCADE)
#     location_title = models.CharField(max_length=100)
#     region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
#     city = models.CharField(max_length=100, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     point = geomodels.PointField(geography=True, blank=True, null=True)

#     def __str__(self):
#         return f'{self.service.title} - {self.city}'

# class WorkingHour(models.Model):
#     DAYS_OF_WEEK = [
#         (0, 'Pirmdiena'),
#         (1, 'Otrdiena'),
#         (2, 'Trešdiena'),
#         (3, 'Ceturtdiena'),
#         (4, 'Piektdiena'),
#         (5, 'Sestdiena'),
#         (6, 'Svētdiena'),
#     ]

#     location = models.ForeignKey(Location, related_name='working_hours', on_delete=models.CASCADE)
#     day = models.IntegerField(choices=DAYS_OF_WEEK)
#     from_hour = models.TimeField()
#     to_hour = models.TimeField()

#     class Meta:
#         unique_together = ('location', 'day')
#         ordering = ['day']

#     def __str__(self):
#         return f'{self.location.city} - {self.get_day_display()}: {self.from_hour}–{self.to_hour}'

# class UserServiceFavorites(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_favorites")
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="favorited_by")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['user', 'service'], name='unique_user_service')
#         ]

#     def __str__(self):
#         return f"{self.user.username} - {self.service.id}"
