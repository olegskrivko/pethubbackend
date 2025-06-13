from django.db import models
from django.conf import settings
from django.utils import timezone
# from services.models import Service


class Pet(models.Model):
    STATUS_CHOICES = [
        (1, 'Pazudis'), # Lost
        (2, 'Atrasts'), # Found
        (3, 'Redzēts'), # Seen
    ]
    SIZE_CHOICES = [
        (1, 'Mazs'), # Small
        (2, 'Vidējs'), # Medium
        (3, 'Liels'), # Large
    ]
    GENDER_CHOICES = [
        (1, 'Tēviņš'), # Male
        (2, 'Mātīte'), # Female
    ]
    BEHAVIOR_CHOICES = [
        (1, 'Draudzīgs'), # Friendly  
        (2, 'Agresīvs'), # Aggressive
        (3, 'Mierīgs'), # Calm
        (4, 'Bailīgs'), # Fearful
        (5, 'Paklausīgs'), # Obedient
    ]
    SPECIES_CHOICES = [
        (1, 'Suns'), # Dog
        (2, 'Kaķis'), # Cat
        (3, 'Cits'), # Other
    ]
    AGE_CHOICES = [
        (1, 'Mazulis'), # Young
        (2, 'Pieaugušais'), # Adult
        (3, 'Seniors'), # Senior
    ]
    PATTERN_CHOICES = [
        (1, 'Vienkrāsains'), # Solid
        (2, 'Strīpains'), # Striped
        (3, 'Punktveida'), # Spotted
        (4, 'Plankumains'), # Patched
        (5, 'Raibs'), # Marbled
    ]
    COLOR_CHOICES = [
        (1, 'Melns'), # Black
        (2, 'Pelēks'), # Gray
        (3, 'Balts'), # White
        (4, 'Krēmīgs'), # Cream
        (5, 'Dzeltens'), # Yellow
        (6, 'Zeltains'), # Golden
        (7, 'Brūns'), # Brown
        (8, 'Sarkans'), # Red
        (9, 'Lillīgs'), # Lilac
        (10, 'Zils'), # Blue
        (11, 'Zaļš'), # Green
        (12, 'Haki'), # Khaki
        (13, 'Bēšīgs'), # Beige
        (14, 'Dzeltenbrūns'), # Fawn
        (15, 'Kaštanbrūns'), # Chestnut
    ]
    PHONE_CODE_CHOICES = [
        (371, 'LV (+371)'), # Latvia
        (370, 'LT (+370)'), # Lithuania
        (372, 'EE (+372)'), # Estonia
    ]

    FINAL_STATUS_CHOICES = [
        (1, 'Nav atrisināts'),           # Open / No Update
        (2, 'Atgriezts saimniekam'),     # Reunited with Owner
        (3, 'Nodots patversmei'),        # Taken to Shelter
        (4, 'Joprojām tiek meklēts'),    # Still Missing / Owner Still Searching
        (5, 'Nav aktuāli'),              # No Longer Relevant
        (6, 'Atradies miris'),           # Deceased
        (7, 'Saimnieks neatrasts'),      # Owner Not Found
    ]

    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Vārds")
    identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID")
    behavior = models.IntegerField(choices=BEHAVIOR_CHOICES, blank=True, null=True, verbose_name="Uzvedība")
    size = models.IntegerField(choices=SIZE_CHOICES, blank=True, null=True, verbose_name="Izmērs")
    age = models.IntegerField(choices=AGE_CHOICES, blank=True, null=True, verbose_name="Vecums")
    gender = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Dzimums")
    species = models.IntegerField(choices=SPECIES_CHOICES, blank=False, null=False, verbose_name="Suga")
    status = models.IntegerField(choices=STATUS_CHOICES, verbose_name="Statuss")
    pattern = models.IntegerField(choices=PATTERN_CHOICES, blank=True, null=True, verbose_name="Kažoka raksts")
    primary_color = models.IntegerField(choices=COLOR_CHOICES, blank=True, null=True, verbose_name="Pamatkrāsa")
    secondary_color = models.IntegerField(choices=COLOR_CHOICES, blank=True, null=True, verbose_name="Sekundārā krāsa")
    notes = models.TextField(blank=True, null=True, verbose_name="Piezīmes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ziņots")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact_phone = models.CharField(max_length=8, blank=True, null=True, verbose_name="Kontakttālrunis")
    phone_code = models.IntegerField(choices=PHONE_CODE_CHOICES, blank=True, null=True, verbose_name="Telefona kods")
    breed = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sķirne")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Ģeogrāfiskais platums")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Ģeogrāfiskais garums")
    pet_image_1 = models.URLField(max_length=255, null=False, blank=False, verbose_name="Mājdzīvnieka 1. attēls")
    pet_image_2 = models.URLField(max_length=255, null=True, blank=True, verbose_name="Mājdzīvnieka 2. attēls")
    pet_image_3 = models.URLField(max_length=255, null=True, blank=True, verbose_name="Mājdzīvnieka 3. attēls")
    pet_image_4 = models.URLField(max_length=255, null=True, blank=True, verbose_name="Mājdzīvnieka 4. attēls")
    event_occurred_at = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name="Notikuma laiks")


    is_public = models.BooleanField(default=True, verbose_name="Vai ir publisks?")
    is_verified = models.BooleanField(default=False, verbose_name="Vai ir pārbaudīts?")


    final_status = models.IntegerField(choices=FINAL_STATUS_CHOICES, default=1, verbose_name="Galīgais statuss")
    # pet_image = models.URLField(max_length=255, blank=False, null=False, verbose_name="Mājdzīvnieka attēls")


    class Meta:
        verbose_name = "Mājdzīvnieks"
        verbose_name_plural = "Mājdzīvnieki"

    def __str__(self):
        return f"Pet {self.id}"
    
    # def get_status_display(self):
    #     return dict(self.STATUS_CHOICES).get(self.status)

    # def get_species_display(self):
    #     return dict(self.SPECIES_CHOICES).get(self.species)
    

class PetSightingHistory(models.Model):
    STATUS_CHOICES = [
        (1, 'Atrasts'), # Found
        (2, 'Redzēts'), # Seen
    ]

    status = models.IntegerField(choices=STATUS_CHOICES, default=2, verbose_name="Statuss")
    event_occurred_at = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name="Notikuma laiks")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ziņots")
    pet = models.ForeignKey('Pet', on_delete=models.CASCADE, related_name='sightings_history')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Ģeogrāfiskais platums")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Ģeogrāfiskais garums")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Ziņotājs")
    notes = models.TextField(blank=True, null=True, verbose_name="Piezīmes")
    pet_image = models.URLField(max_length=255, null=False, blank=False, verbose_name="Mājdzīvnieka attēls")
    is_public = models.BooleanField(default=True, verbose_name="Vai ir publisks?")
    is_verified = models.BooleanField(default=False, verbose_name="Vai ir pārbaudīts?")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mājdzīvnieka novērojums"
        verbose_name_plural = "Mājdzīvnieka novērojumi"

    def __str__(self):
        return f"{self.pet.id} - {self.get_status_display()} at {self.created_at}"


class UserFavorites(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['user', 'pet'], name='unique_user_pet')
    ]

    def __str__(self):
        return f"{self.user.username} - {self.pet.id}"


