from django.core.management.base import BaseCommand
from faker import Faker
from decimal import Decimal
import random
from django.contrib.auth import get_user_model
from services.models import Service, Location, Review

fake = Faker("lv_LV")  # Latvian locale
User = get_user_model()

class Command(BaseCommand):
    help = "Generate fake pet-related services with locations and images"

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR("❌ No users found. Please create users first."))
            return

        def get_choice(choices):
            return random.choice([c[0] for c in choices])

        for _ in range(10):
            user = random.choice(users)
            title = fake.catch_phrase()
            description = fake.paragraph(nb_sentences=4)
            price = round(random.uniform(5, 100), 2)
            price_type = get_choice(Service.PRICE_TYPE_CHOICES)
            category = get_choice(Service.SERVICE_CATEGORIES)
            provider_type = get_choice(Service.PROVIDER_TYPES)
            phone_code = get_choice(Service.PHONE_CODE_CHOICES)

            # Simulate pet-themed images
            image_url = "https://picsum.photos/600/400"

            service = Service.objects.create(
                user=user,
                title=title,
                description=description,
                price=price,
                price_type=price_type,
                category=category,
                is_active=True,
                is_available=random.choice([True, False]),
                provider_type=provider_type,
                service_image_1=image_url,
                service_image_2=image_url,
                service_image_3=image_url,
                service_image_4=image_url,
                website=fake.url(),
                is_online=random.choice([True, False]),
                phone_number=fake.msisdn()[-8:],
                phone_code=phone_code,
                email=fake.email()
            )

            # Create related location in Latvia
            Location.objects.create(
                service=service,
                location_title=fake.company(),
                location_description=fake.text(max_nb_chars=150),
                region="Latvija",
                city=fake.city(),
                street=fake.street_name(),
                postal_code=fake.postcode(),
                full_address=fake.address(),
                latitude=Decimal(random.uniform(55.6, 58.1)),
                longitude=Decimal(random.uniform(20.9, 28.3)),
            )

            # Optionally create a few reviews
            for _ in range(random.randint(1, 3)):
                Review.objects.create(
                    service=service,
                    user=random.choice(users),
                    rating=Decimal(str(random.uniform(2.5, 5.0))).quantize(Decimal("0.1")),
                    comment=fake.sentence(),
                    is_approved=True
                )

            self.stdout.write(f"✅ Created service: {service.title} (User: {user.username})")

        self.stdout.write(self.style.SUCCESS("🎉 Successfully created 10 fake services"))
