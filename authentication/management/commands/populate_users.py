from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from faker import Faker
from authentication.utils import generate_uuid_username 
from django.contrib.auth import get_user_model
User = get_user_model()

fake = Faker()

class Command(BaseCommand):
    help = "Generate 20 fake users with unique pet-themed usernames and avatars"

    def handle(self, *args, **kwargs):
        for _ in range(20):
            email = fake.unique.email()
            password = get_random_string(10)

            # Use your custom generator for username + avatar
            username, avatar = generate_uuid_username()

            user = User.objects.create_user(
                email=email,
                password=password,
                username=username,
                avatar=avatar,
                is_active=True,
                is_verified=True,
            )

            self.stdout.write(f"✅ Created {email} | {username} | Avatar: {avatar} | Password: {password}")

        self.stdout.write(self.style.SUCCESS("🎉 Successfully created 20 fake users"))