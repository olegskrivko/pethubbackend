from django.db import models
from django.contrib.postgres.fields import ArrayField


# ============================================================================
# SHELTER MODELS
# ============================================================================

class AnimalType(models.Model):
    """Model for categorizing types of animals that shelters can accommodate."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class SocialMedia(models.Model):
    """Model for storing social media platform information."""
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
    profile_url = models.URLField()
    is_official = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return dict(self.PLATFORM_CHOICES).get(self.platform, "Unknown Platform")


class Shelter(models.Model):
    """Model for storing comprehensive shelter information."""
    
    # Choice definitions
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

    # Basic information
    animal_types = models.ManyToManyField(AnimalType, blank=True, related_name='shelters', verbose_name="Animal types")
    name = models.CharField(max_length=200, verbose_name="Nosaukums")
    description = models.TextField(blank=True, null=True, verbose_name="Apraksts")
    website = models.URLField(blank=True, null=True, verbose_name="Vietne")
    size = models.IntegerField(choices=SHELTER_SIZE_CHOICES, blank=True, null=True, verbose_name="Izmērs")
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True, null=True, verbose_name="Valsts")
    category = models.IntegerField(choices=SHELTER_CATEGORY_CHOICES, blank=True, null=True, verbose_name="Kategorija")
    
    # Services and policies
    is_public = models.BooleanField(default=True, verbose_name="Atvērts sabiedrībai")
    offers_adoption = models.BooleanField(default=False, verbose_name="Piedāvā adopciju")
    accepts_volunteers = models.BooleanField(default=False, verbose_name="Pieņem brīvprātīgos")
    accepts_donations = models.BooleanField(default=False, verbose_name="Pieņem ziedojumus")

    # Location information
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Reģions")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pilsēta")
    street = models.CharField(max_length=200, blank=True, null=True, verbose_name="Iela")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Pasta indekss")
    full_address = models.TextField(blank=True, null=True, verbose_name="Adrese")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Ģeogrāfiskais platums")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, verbose_name="Ģeogrāfiskais garums")

    # Contact information
    social_media = models.ManyToManyField(SocialMedia, blank=True, related_name='shelters', verbose_name="Sociālie mediji")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefona numurs")
    phone_code = models.CharField(max_length=4, choices=PHONE_CODE_CHOICES, blank=True, null=True, verbose_name="Telefona kods")
    email = models.EmailField(blank=True, null=True, verbose_name="E-pasts")

    def formatted_phone_code(self):
        """Return formatted phone code with plus sign."""
        return f"+{self.phone_code}" if self.phone_code else ""

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Automatically generate full address if all components are present."""
        if all([self.street, self.city, self.country]):
            self.full_address = f"{self.street}, {self.city}, {self.region or ''}, {self.country} - {self.postal_code or ''}".strip(', -')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Shelter"
        verbose_name_plural = "Shelters"
        ordering = ['name']