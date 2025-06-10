from django.db import models

# Create your models here.
# articles/models.py
from django.db import models
from django.utils.text import slugify
# from django.contrib.auth.models import User
from django.conf import settings
# from taggit.managers import TaggableManager
from cloudinary.models import CloudinaryField  # Import CloudinaryField

class Article(models.Model):
    title = models.CharField(max_length=200, unique=True)
    summary = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    public = models.BooleanField(default=False)

    # Future-proofing:
    # cover_image = CloudinaryField('image', blank=True, null=True)  # For a main article banner
    # language = models.CharField(max_length=10, default='lv')  # If you want multilingual support later
    # seo_description = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Paragraph(models.Model):
    article = models.ForeignKey(Article, related_name="paragraphs", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    #image = models.ImageField(upload_to='article_images/', blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)  # Use CloudinaryField for image storage
    #image = models.URLField(blank=True, null=True)

    text = models.TextField()
    order = models.IntegerField(default=0)
    image_prompt = models.TextField()
    # Optional AI-generated metadata
    # image_prompt = models.TextField(blank=True, null=True)  # For tracking AI prompt used
    # ai_generated = models.BooleanField(default=False)       # Optional flag
    # audio = CloudinaryField('audio', blank=True, null=True) # If you want TTS playback for accessibility

    def __str__(self):
        return f'{self.article.title} - {self.title}'

    class Meta:
        ordering = ['order']
