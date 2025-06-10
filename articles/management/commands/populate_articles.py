from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
import random
from django.contrib.auth import get_user_model

from articles.models import Article, Paragraph

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = "Generate fake articles with paragraphs"

    def handle(self, *args, **kwargs):
        # Make sure you have at least one user in the system
        authors = list(User.objects.all())
        if not authors:
            self.stdout.write(self.style.ERROR("❌ No users found. Create a user first to assign as article author."))
            return

        for _ in range(10):  # Create 10 articles
            title = fake.sentence(nb_words=6)
            summary = fake.paragraph(nb_sentences=3)
            author = random.choice(authors)

            article = Article.objects.create(
                title=title,
                summary=summary,
                author=author,
                public=random.choice([True, False]),
                published_at=fake.date_time_this_year()
            )

            paragraph_count = random.randint(2, 5)
            for i in range(paragraph_count):
                para_title = fake.sentence(nb_words=4)
                para_text = fake.paragraph(nb_sentences=5)
                image_prompt = fake.sentence(nb_words=7)
                # Placeholder image logic (optional)
                #image_url = f"https://placehold.co/600x400?text={slugify(para_title)}"

                Paragraph.objects.create(
                    article=article,
                    title=para_title,
                    text=para_text,
                    order=i,
                    image_prompt=image_prompt,
                   # image=image_url,
                )

            self.stdout.write(f"✅ Created article: {article.title} with {paragraph_count} paragraphs")

        self.stdout.write(self.style.SUCCESS("🎉 Successfully generated 10 fake articles"))
