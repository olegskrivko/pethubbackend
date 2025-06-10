from django.contrib import admin
from .models import Article, Paragraph

class ParagraphInline(admin.TabularInline):
    model = Paragraph
    extra = 1  # Number of empty paragraph forms
    fields = ('title', 'image', 'text', 'order')  # Customize the fields displayed in the inline
    # Adding the image_url method in the Inline
    def image_url(self, obj):
        if obj.image:
            return obj.image.url  # Return the URL of the Cloudinary image
        return 'No image'

    image_url.short_description = 'Image URL'  # Set column name for the image URL
    readonly_fields = ['image_url']  # Ensure this field is read-only

class ArticleAdmin(admin.ModelAdmin):
    inlines = [ParagraphInline]
    list_display = ('title', 'created_at', 'updated_at', 'public')  # ✅ Show public status
    #search_fields = ('title', 'summary', 'tags__name')  # ✅ Allow searching by tags
    #list_filter = ('public', 'created_at', 'tags')  # ✅ Add filters for better navigation
    prepopulated_fields = {"slug": ("title",)}  # ✅ Auto-generate slugs from title
    ordering = ('-created_at',)  # ✅ Show newest articles first
    list_per_page = 20  # Show 20 articles per page for better navigation

     # Adding the image_url method for ArticleAdmin if needed (for image related fields)
    def image_url(self, obj):
        if obj.paragraphs.filter(image__isnull=False).exists():
            # This will check if there is an image in any of the paragraphs and return the first one
            first_paragraph_with_image = obj.paragraphs.filter(image__isnull=False).first()
            return first_paragraph_with_image.image.url  # Return the URL of the image uploaded to Cloudinary
        return 'No image'

    image_url.short_description = 'First Paragraph Image URL'  # Set column name for the image URL

admin.site.register(Article, ArticleAdmin)
