# Create your models here.
# services/models.py
from django.db import models
from django.contrib.auth import get_user_model
# from core.models import SocialMedia
from django.conf import settings
from django.db.models import Avg
User = get_user_model()
    
class Service(models.Model):
    SERVICE_CATEGORIES = [
        (1, 'Dzīvnieku pieskatīšana'),        # Pet Sitting
        (2, 'Suņu pastaigas'),                # Dog Walking
        (3, 'Kopšana'),                       # Grooming
        (4, 'Apmācība'),                      # Training
        (5, 'Izmitināšana'),                  # Boarding
        (6, 'Veterinārārsts'),                # Veterinary
        (7, 'Foto sesijas'),                  # Pet Photography
        (8, 'Glābšana un meklēšana'),         # Pet Rescue and Search
        (9, 'Piederumi un aksesuāri'),        # Pet Supplies and Accessories
        (10, 'Māksla'),                       # Pet Art
        (11, 'Apbedīšana'),                   # Pet Burial Services
        (12, 'Transports'),                   # Pet Transportation
        (13, 'Audzētavas'),                   # Pet Breeders
        (14, 'Apdrošināšana'),                # Pet Insurance
        (15, 'Citi pakalpojumi'),             # Miscellaneous
    ]
    PROVIDER_TYPES = [
        (1, 'Fiziska persona'),    # Physical Person
        (2, 'Juridiska persona'),  # Legal Entity (Company)
    ]

    PHONE_CODE_CHOICES = [
        (371, 'LV (+371)'), # Latvia
        (370, 'LT (+370)'), # Lithuania
        (372, 'EE (+372)'), # Estonia
    ]
    PRICE_TYPE_CHOICES = [
        (1, 'Stundā'),
        (2, 'Vienībā'),
        (3, 'Dienā'),
        (4, 'Pēc vienošanās'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_type = models.IntegerField(choices=PRICE_TYPE_CHOICES, default=1)    
    category = models.IntegerField(choices=SERVICE_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 
    is_available = models.BooleanField(default=True)
    provider_type = models.IntegerField(choices=PROVIDER_TYPES)
    service_image_1 = models.URLField(max_length=255, null=False, blank=False, verbose_name="Servisa 1. attēls")
    service_image_2 = models.URLField(max_length=255, null=True, blank=True, verbose_name="Servisa 2. attēls")
    service_image_3 = models.URLField(max_length=255, null=True, blank=True, verbose_name="Servisa 3. attēls")
    service_image_4 = models.URLField(max_length=255, null=True, blank=True, verbose_name="Servisa 4. attēls")
    website = models.URLField(blank=True, null=True, verbose_name="Vietne")
    # social_media = models.ManyToManyField(SocialMedia, blank=True, related_name='services', verbose_name="Sociālie mediji")
    is_online = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefona numurs")
    phone_code = models.CharField(max_length=5, null=True, blank=True, choices=PHONE_CODE_CHOICES, verbose_name="Telefona kods")
    email = models.EmailField(blank=True, null=True, verbose_name="E-pasts")

    def average_rating(self):
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

    def review_count(self):
        return self.reviews.count()
    
    def __str__(self):
        return self.title
    
class Review(models.Model):
    service = models.ForeignKey(Service, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)  # 0.0 to 5.0
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ('service', 'user')
    
class Location(models.Model):
    service = models.ForeignKey(Service, related_name='locations', on_delete=models.CASCADE)
    location_title = models.CharField(max_length=100)
    location_description = models.TextField()
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Reģions")  # State/Province
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pilsēta")
    street = models.CharField(max_length=200, blank=True, null=True, verbose_name="Iela")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Pasta indekss")
    full_address = models.TextField(blank=True, null=True, verbose_name="Adrese")  # Optional, for storing formatted address
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Ģeogrāfiskais platums")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Ģeogrāfiskais garums")

    def __str__(self):
        return f'{self.service.title} - {self.city}'
    


# class WorkingHour(models.Model):
#     DAYS_OF_WEEK = [
#         (0, 'Pirmdiena'), # Monday
#         (1, 'Otrdiena'), # Tuesday
#         (2, 'Trešdiena'), # Wednesday
#         (3, 'Ceturtdiena'), # Thursday
#         (4, 'Piektdiena'), # Friday
#         (5, 'Sestdiena'), # Saturday
#         (6, 'Svētdiena'), # Sunday
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

class UserServiceFavorites(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_favorites")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'service'], name='unique_user_service')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.service.id}"
