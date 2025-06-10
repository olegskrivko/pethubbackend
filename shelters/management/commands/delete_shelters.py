from django.core.management.base import BaseCommand
from shelters.models import Shelter

class Command(BaseCommand):
    help = "Delete all shelters from the database"

    def handle(self, *args, **kwargs):
        count = Shelter.objects.count()
        if count == 0:
            self.stdout.write("No shelters found to delete.")
            return

        # Delete all shelters
        Shelter.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully deleted {count} shelters"))
# from django.core.management.base import BaseCommand
# from shelters.models import Shelter, SocialMedia

# class Command(BaseCommand):
#     help = "Delete all shelters and their associated social media entries"

#     def handle(self, *args, **kwargs):
#         shelters = Shelter.objects.all()
#         shelter_count = shelters.count()

#         if shelter_count == 0:
#             self.stdout.write("No shelters found to delete.")
#             return

#         # Collect all social media linked to these shelters
#         social_media_ids = SocialMedia.objects.filter(shelters__in=shelters).values_list('id', flat=True).distinct()
#         social_media_count = social_media_ids.count()

#         # Delete shelters
#         shelters.delete()
#         self.stdout.write(self.style.SUCCESS(f"✅ Successfully deleted {shelter_count} shelters"))

#         # Delete associated social media
#         if social_media_count > 0:
#             SocialMedia.objects.filter(id__in=social_media_ids).delete()
#             self.stdout.write(self.style.SUCCESS(f"✅ Successfully deleted {social_media_count} associated social media entries"))
#         else:
#             self.stdout.write("No social media entries associated with shelters found to delete.")
