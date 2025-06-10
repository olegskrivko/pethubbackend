# from django.core.management.base import BaseCommand
# from faker import Faker
# import random

# from shelters.models import Shelter, SocialMedia, AnimalType  # import AnimalType

# fake = Faker()

# class Command(BaseCommand):
#     help = "Generate 20 fake shelters with optional social media links and animal types"

#     def handle(self, *args, **kwargs):
#         COUNTRY_CHOICES = ['LV', 'EE', 'LT']
#         PHONE_CODES = ['371', '370', '372']
#         PLATFORM_CHOICES = dict(SocialMedia.PLATFORM_CHOICES)

#         # Get all animal types from DB
#         animal_types = list(AnimalType.objects.all())
#         if not animal_types:
#             self.stdout.write(self.style.ERROR("No AnimalType objects found. Please populate AnimalType first."))
#             return

#         for _ in range(20):
#             name = f"{fake.company()} Shelter"
#             description = fake.text(max_nb_chars=200)
#             website = fake.url()
#             country = random.choice(COUNTRY_CHOICES)
#             region = fake.state()
#             city = fake.city()
#             street = fake.street_address()
#             postal_code = fake.postcode()
#             latitude = round(fake.latitude(), 6)
#             longitude = round(fake.longitude(), 6)
#             phone_number = fake.phone_number()
#             phone_code = random.choice(PHONE_CODES)
#             email = fake.company_email()

#             # Create Shelter instance
#             shelter = Shelter.objects.create(
#                 name=name,
#                 description=description,
#                 website=website,
#                 country=country,
#                 region=region,
#                 city=city,
#                 street=street,
#                 postal_code=postal_code,
#                 latitude=latitude,
#                 longitude=longitude,
#                 phone_number=phone_number,
#                 phone_code=phone_code,
#                 email=email
#             )

#             # Add random social media accounts (0–3)
#             for _ in range(random.randint(0, 3)):
#                 platform = random.choice(list(PLATFORM_CHOICES.keys()))
#                 sm = SocialMedia.objects.create(
#                     platform=platform,
#                     profile_url=fake.url(),
#                     is_official=random.choice([True, False]),
#                     is_verified=random.choice([True, False])
#                 )
#                 shelter.social_media.add(sm)

#             # Add at least one animal type, possibly more
#             selected_animal_types = random.sample(animal_types, k=random.randint(1, min(3, len(animal_types))))
#             shelter.animal_types.add(*selected_animal_types)

#             self.stdout.write(f"✅ Created shelter: {shelter.name} with {len(selected_animal_types)} animal types")

#         self.stdout.write(self.style.SUCCESS("🎉 Successfully created 20 fake shelters with animal types"))
from django.core.management.base import BaseCommand
from faker import Faker
import random

from shelters.models import Shelter, SocialMedia, AnimalType

fake = Faker()

class Command(BaseCommand):
    help = "Generate 20 fake shelters with optional social media links and animal types"

    def handle(self, *args, **kwargs):
        COUNTRY_CHOICES = ['LV', 'EE', 'LT']
        PHONE_CODES = ['371', '370', '372']
        PLATFORM_CHOICES = dict(SocialMedia.PLATFORM_CHOICES)

        CATEGORY_CHOICES = [choice[0] for choice in Shelter.SHELTER_CATEGORY_CHOICES]
        SIZE_CHOICES = [choice[0] for choice in Shelter.SHELTER_SIZE_CHOICES]

        animal_types = list(AnimalType.objects.all())
        if not animal_types:
            self.stdout.write(self.style.ERROR("❌ No AnimalType objects found. Please populate AnimalType first."))
            return

        for _ in range(20):
            name = f"{fake.company()} Shelter"
            description = fake.text(max_nb_chars=200)
            website = fake.url()
            country = random.choice(COUNTRY_CHOICES)
            region = fake.state()
            city = fake.city()
            street = fake.street_address()
            postal_code = fake.postcode()
            latitude = round(fake.latitude(), 6)
            longitude = round(fake.longitude(), 6)
            phone_number = fake.phone_number()
            phone_code = random.choice(PHONE_CODES)
            email = fake.company_email()

            category = random.choice(CATEGORY_CHOICES)
            size = random.choice(SIZE_CHOICES)
            is_public = random.choice([True, False])
            offers_adoption = random.choice([True, False])
            accepts_volunteers = random.choice([True, False])
            accepts_donations = random.choice([True, False])

            shelter = Shelter.objects.create(
                name=name,
                description=description,
                website=website,
                country=country,
                region=region,
                city=city,
                street=street,
                postal_code=postal_code,
                latitude=latitude,
                longitude=longitude,
                phone_number=phone_number,
                phone_code=phone_code,
                email=email,
                category=category,
                size=size,
                is_public=is_public,
                offers_adoption=offers_adoption,
                accepts_volunteers=accepts_volunteers,
                accepts_donations=accepts_donations
            )

            for _ in range(random.randint(0, 3)):
                platform = random.choice(list(PLATFORM_CHOICES.keys()))
                sm = SocialMedia.objects.create(
                    platform=platform,
                    profile_url=fake.url(),
                    is_official=random.choice([True, False]),
                    is_verified=random.choice([True, False])
                )
                shelter.social_media.add(sm)

            selected_animal_types = random.sample(animal_types, k=random.randint(1, min(3, len(animal_types))))
            shelter.animal_types.add(*selected_animal_types)

            self.stdout.write(f"✅ Created shelter: {shelter.name} with {len(selected_animal_types)} animal types")

        self.stdout.write(self.style.SUCCESS("🎉 Successfully created 20 fake shelters with all fields"))
