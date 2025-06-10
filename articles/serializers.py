# articles/serializers.py
# serializers.py
# from django.contrib.auth.models import User 
from rest_framework import serializers
from .models import Article, Paragraph
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Include fields you want to display

class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ['id', 'title', 'image', 'text']

class ArticleSerializer(serializers.ModelSerializer):
    paragraphs = ParagraphSerializer(many=True)  # Nested serializer for paragraphs
    author = UserSerializer(read_only=True)  # Add the UserSerializer here
    class Meta:
        model = Article
        fields = ['id', 'title', 'summary', 'created_at', 'updated_at', 'slug', 'paragraphs', 'published_at', 'author']
