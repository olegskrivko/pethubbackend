from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.contrib.postgres.fields import ArrayField  # If you use PostgreSQL, otherwise JSONField is recommended

class AnimalType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class SocialMedia(models.Model):
    # Defining the available platforms as a set of choices
    PLATFORM_CHOICES = [
        (1, 'Facebook'),
        (2, 'Instagram'),
        (3, 'X'),
        (4, 'LinkedIn'),
        (5, 'YouTube'),
        (6, 'TikTok'),
        (7, 'Pinterest'),
        (8, 'Snapchat'),
    ]
    platform = models.IntegerField(choices=PLATFORM_CHOICES, blank=False, null=False, verbose_name="Platforma")
    profile_url = models.URLField()  # URL of the profile
    is_official = models.BooleanField(default=False)  # Whether it's an official profile (e.g., government, embassy)
    is_verified = models.BooleanField(default=False)  # Whether the profile is verified (default to False)

    def __str__(self):
        return dict(self.PLATFORM_CHOICES).get(self.platform, "Unknown Platform")

class Shelter(models.Model):

    # Define predefined choices for phone codes
    PHONE_CODE_CHOICES = [
    ('371', 'LV (+371)'),
    ('370', 'LT (+370)'),
    ('372', 'EE (+372)'),
    ]

    COUNTRY_CHOICES = [
        ('LV', 'Latvija'),
        ('EE', 'Igaunija'),
        ('LT', 'Lietuva'),
    ]
    
    SHELTER_CATEGORY_CHOICES = [
        (1, 'Municipal Shelter'),
        (2, 'Animal Rescue'),
        (3, 'Sanctuary'),
        (4, 'Private Shelter'),
        (5, 'Other'),
    ]
    SHELTER_SIZE_CHOICES = [
    (1, 'Small (1-20 animals)'),
    (2, 'Medium (21-100 animals)'),
    (3, 'Large (100+ animals)'),
    ]

    animal_types = models.ManyToManyField(AnimalType, blank=True, related_name='shelters', verbose_name="Animal types")
    name = models.CharField(max_length=200, verbose_name="Nosaukums")
    description = models.TextField(blank=True, null=True, verbose_name="Apraksts")
    website = models.URLField(blank=True, null=True, verbose_name="Vietne")
    size = models.IntegerField(choices=SHELTER_SIZE_CHOICES, blank=True, null=True, verbose_name="Izmērs")

    # Use predefined choices for the country field
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True, null=True, verbose_name="Valsts")

    category = models.IntegerField(choices=SHELTER_CATEGORY_CHOICES, blank=True, null=True, verbose_name="Kategorija") 
    is_public = models.BooleanField(default=True, verbose_name="Atvērts sabiedrībai")
    offers_adoption = models.BooleanField(default=False, verbose_name="Piedāvā adopciju")
    accepts_volunteers = models.BooleanField(default=False, verbose_name="Pieņem brīvprātīgos")
    accepts_donations = models.BooleanField(default=False, verbose_name="Pieņem ziedojumus")

    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Reģions")  # State/Province
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pilsēta")
    street = models.CharField(max_length=200, blank=True, null=True, verbose_name="Iela")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Pasta indekss")
    full_address = models.TextField(blank=True, null=True, verbose_name="Adrese")  # Optional, for storing formatted address

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Ģeogrāfiskais platums")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Ģeogrāfiskais garums")

     # Social Media
    #social_media = models.ManyToManyField(SocialMedia, blank=True, related_name='shelters', verbose_name="Sociālie mediji")
    #social_media = models.JSONField(default=list, blank=True, verbose_name="Sociālie mediji")
    # Social Media: Multiple social media platforms can be chosen
    social_media = models.ManyToManyField(SocialMedia, blank=True, related_name='shelters', verbose_name="Sociālie mediji")

    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefona numurs")
    phone_code = models.CharField(max_length=4, choices=PHONE_CODE_CHOICES, blank=True, null=True, verbose_name="Telefona kods")

    email = models.EmailField(blank=True, null=True, verbose_name="E-pasts")

    def formatted_phone_code(self):
        return f"+{self.phone_code}" if self.phone_code else ""

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        #Automatically generate full address if all components are present
        if all([self.street, self.city, self.country]):
            self.full_address = f"{self.street}, {self.city}, {self.region or ''}, {self.country} - {self.postal_code or ''}".strip(', -')
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Shelter"
        verbose_name_plural = "Shelters"
        ordering = ['name']