from django.db import models
from django.utils.text import slugify
from django.conf import settings
from cloudinary.models import CloudinaryField


# ============================================================================
# ARTICLE MODELS
# ============================================================================

class Article(models.Model):
    """
    Model for storing article content with metadata.
    """
    title = models.CharField(max_length=200, unique=True)
    summary = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    public = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Paragraph(models.Model):
    """
    Model for storing paragraph content within articles.
    Supports images and ordering.
    """
    article = models.ForeignKey(Article, related_name="paragraphs", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = CloudinaryField('image', blank=True, null=True)
    text = models.TextField()
    order = models.IntegerField(default=0)
    image_prompt = models.TextField()

    def __str__(self):
        return f'{self.article.title} - {self.title}'

    class Meta:
        ordering = ['order']
