from django.core.management.base import BaseCommand
from pets.models import Pet, PetSightingHistory, UserFavorites

class Command(BaseCommand):
    help = "Delete all pets and related pet data"

    def handle(self, *args, **kwargs):
        sighting_count, _ = PetSightingHistory.objects.all().delete()
        fav_count, _ = UserFavorites.objects.all().delete()
        pet_count, _ = Pet.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            f"🗑️ Deleted {pet_count} pets, {sighting_count} sightings, and {fav_count} favorites."
        ))
