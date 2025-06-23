# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from faker import Faker
# import random
# from django.contrib.auth import get_user_model

# from pets.models import Pet  # adjust import if your app name is different

# fake = Faker()
# User = get_user_model()

# class Command(BaseCommand):
#     help = "Generate fake pets"

#     def handle(self, *args, **kwargs):
#         authors = list(User.objects.all())
#         if not authors:
#             self.stdout.write(self.style.ERROR("❌ No users found. Create a user first to assign as pet author."))
#             return

#         for _ in range(10):  # Create 10 pets
#             name = fake.first_name()
#             identifier = fake.uuid4()
#             species = random.choice([1, 2, 3])
#             status = random.choice([1, 2, 3])
#             behavior = random.choice([1, 2, 3, 4, 5])
#             size = random.choice([1, 2, 3])
#             age = random.choice([1, 2, 3])
#             gender = random.choice([1, 2])
#             pattern = random.choice([1, 2, 3, 4, 5])
#             primary_color = random.choice(range(1, 16))
#             secondary_color = random.choice(range(1, 16))
#             notes = fake.text(max_nb_chars=200)
#             contact_phone = fake.msisdn()[-8:]  # Last 8 digits simulating a phone number
#             phone_code = random.choice([371, 370, 372])
#             breed = fake.word()
#             latitude = fake.latitude()
#             longitude = fake.longitude()
#             pet_image_1 = fake.image_url(width=600, height=400)
#             pet_image_2 = fake.image_url(width=600, height=400)
#             pet_image_3 = fake.image_url(width=600, height=400)
#             pet_image_4 = fake.image_url(width=600, height=400)

#             event_time_naive = fake.date_time_this_year()
#             event_occurred_at = timezone.make_aware(event_time_naive)

#             author = random.choice(authors)

#             pet = Pet.objects.create(
#                 name=name,
#                 identifier=identifier,
#                 species=species,
#                 status=status,
#                 behavior=behavior,
#                 size=size,
#                 age=age,
#                 gender=gender,
#                 pattern=pattern,
#                 primary_color=primary_color,
#                 secondary_color=secondary_color,
#                 notes=notes,
#                 contact_phone=contact_phone,
#                 phone_code=phone_code,
#                 breed=breed,
#                 latitude=latitude,
#                 longitude=longitude,
#                 pet_image_1=pet_image_1,
#                 pet_image_2=pet_image_2,
#                 pet_image_3=pet_image_3,
#                 pet_image_4=pet_image_4,
#                 event_occurred_at=event_occurred_at,
#                 author=author,
#             )

#             self.stdout.write(f"✅ Created pet: {pet.name} (ID: {pet.id})")

#         self.stdout.write(self.style.SUCCESS("🎉 Successfully generated 10 fake pets"))
from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.contrib.auth import get_user_model
from decimal import Decimal
from pets.models import Pet  # Adjust if your app name is different

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = "Generate fake pets with images from picsum.photos"

    def handle(self, *args, **kwargs):
        authors = list(User.objects.all())
        if not authors:
            self.stdout.write(self.style.ERROR("❌ No users found. Create a user first to assign as pet author."))
            return

        # Helper to get random choice from a model field choices
        def get_random_choice(choices):
            return random.choice([choice[0] for choice in choices])

        for _ in range(10):  # Create 10 pets
            author = random.choice(authors)
            final_status = get_random_choice(Pet.FINAL_STATUS_CHOICES)
            is_closed = final_status != 1  # Consider only status 1 as open

            pet = Pet.objects.create(
                name=fake.first_name(),
                identifier=fake.uuid4(),
                behavior=get_random_choice(Pet.BEHAVIOR_CHOICES),
                size=get_random_choice(Pet.SIZE_CHOICES),
                age=get_random_choice(Pet.AGE_CHOICES),
                gender=get_random_choice(Pet.GENDER_CHOICES),
                species=get_random_choice(Pet.SPECIES_CHOICES),
                status=get_random_choice(Pet.STATUS_CHOICES),
                pattern=get_random_choice(Pet.PATTERN_CHOICES),
                primary_color=get_random_choice(Pet.COLOR_CHOICES),
                secondary_color=get_random_choice(Pet.COLOR_CHOICES),
                notes=fake.paragraph(nb_sentences=3),
                author=author,
                contact_phone=fake.msisdn()[:8],
                phone_code=get_random_choice(Pet.PHONE_CODE_CHOICES),
                breed=fake.word(),
                latitude=Decimal(random.uniform(55.6, 58.1)),
                longitude=Decimal(random.uniform(20.9, 28.3)),
                pet_image_1="https://picsum.photos/600/400",
                pet_image_2="https://picsum.photos/600/400",
                pet_image_3="https://picsum.photos/600/400",
                pet_image_4="https://picsum.photos/600/400",
                event_occurred_at=fake.date_time_this_year(),
                is_public=random.choice([True, False]),
                is_verified=random.choice([True, False]),
                final_status=final_status,
                is_closed=is_closed,
            )
            self.stdout.write(f"✅ Created pet: {pet.name} (ID: {pet.identifier})")

        self.stdout.write(self.style.SUCCESS("🎉 Successfully generated 10 fake pets"))
