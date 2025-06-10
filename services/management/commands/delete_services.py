from django.core.management.base import BaseCommand
from services.models import Service

class Command(BaseCommand):
    help = "Delete all services and related data"

    def handle(self, *args, **kwargs):
        count = Service.objects.count()
        Service.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"🧹 Deleted {count} services and all related reviews/locations"))
