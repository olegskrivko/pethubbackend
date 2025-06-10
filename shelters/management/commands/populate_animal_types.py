# populate_animal_types.py

from django.core.management.base import BaseCommand
from shelters.models import AnimalType  # Replace 'yourapp' with your actual app name

class Command(BaseCommand):
    help = 'Populate AnimalType model with default animal tags'

    def handle(self, *args, **kwargs):
        animals = ['Suns', 'Kaķis', 'Papagailis', 'Trusis', 'Kāmis']
        created_count = 0

        for animal in animals:
            obj, created = AnimalType.objects.get_or_create(name=animal)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} animal types.'))
