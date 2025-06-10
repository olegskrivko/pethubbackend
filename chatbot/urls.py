from django.urls import path
from .views import ChatBotAPIView, PetRecommendationAPIView

urlpatterns = [
    path('', ChatBotAPIView.as_view(), name='chatbot'),  # Directly map to the ChatBotAPIView
    path('pet-recommendation/', PetRecommendationAPIView.as_view(), name='pet_recommendation'),  # New route
]
