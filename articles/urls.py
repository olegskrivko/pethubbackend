# articles/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, ParagraphViewSet

# Create a router and register the ArticleViewSet
router = DefaultRouter()

router.register(r'', ArticleViewSet)  # Route for articles
router.register(r'paragraphs', ParagraphViewSet)  # Route for paragraphs (if needed)

urlpatterns = [
    path('', include(router.urls)),  # Maps 'articles/' to the ArticleViewSet
    path('<int:article_id>/paragraphs/', ParagraphViewSet.as_view({'get': 'list'})),  # Fetch paragraphs for an article
]