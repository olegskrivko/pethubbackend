from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from dotenv import load_dotenv
from django.utils.timezone import now, timedelta
from pets.models import Pet
import os
from openai import OpenAI
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import json
from authentication.ratelimit_utils import (
hourly_20_rate_limit
)
#from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# Load environment variables
if os.path.exists("/etc/secrets/.env"):
    load_dotenv("/etc/secrets/.env")
else:
    load_dotenv()  # local .env

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================================
# CHATBOT API VIEW
# ============================================================================

class ChatBotAPIView(APIView):
    """
    AI-powered chatbot for pet search and informational queries.
    Handles both search requests and general pet-related questions.
    """
    
    def post(self, request):
        """
        Process user input and return appropriate response.
        Supports both pet search and informational queries.
        """
        user_input = request.data.get("message", "")

        # Step 1: Classify user intent using AI
        system_prompt = """
You are an assistant for a lost pet search website. Classify the message as either:
- "informational": user is asking general questions about pets or lost/found process.
- "search": user wants to search for pets using filters.

If it's a search, extract a JSON like:
{
  "intent": "search",
  "status": "lost",
  "species": "dog",
  "size": "small",
  "color": "brown",
  "recent_days": 7
}

Supported filters: status, species, size, color, recent_days
Status: lost, found, seen
Species: dog, cat, other
Size: small, medium, large
Color: black, white, brown, etc.

If it's not a search, return:
{ "intent": "informational" }
"""

        try:
            classification_response = client.chat.completions.create(
                model="gpt-4-0613",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )

            gpt_content = classification_response.choices[0].message.content
            gpt_result = json.loads(gpt_content)
        except Exception as e:
            return Response(
                {"type": "error", "reply": "GPT classification error."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Step 2: Handle search intent
        if gpt_result.get("intent") == "search":
            pets = self.search_pets(gpt_result)

            if pets.exists():
                results = [
                    {
                        "status": pet.status,
                        "status_display": pet.get_status_display(),
                        "species": pet.species,
                        "species_display": pet.get_species_display(),
                        "name": pet.name or "Bezvārda dzīvnieks",
                        "image": pet.pet_image_1,
                        "url": f"/pets/{pet.id}"
                    }
                    for pet in pets
                ]
                return Response({"type": "pet_results", "pets": results})
            else:
                return Response({
                    "type": "pet_results", 
                    "pets": [], 
                    "message": "Nekas netika atrasts."
                })

        # Step 3: Handle informational questions
        elif gpt_result.get("intent") == "informational":
            try:
                detailed_system_prompt = (
                    "You are an expert cynologist and veterinarian specializing in dogs and cats. "
                    "Provide helpful, accurate, and relevant information about dogs and cats only. "
                    "Answer clearly and concisely."
                )

                info_response = client.chat.completions.create(
                    model="gpt-4-0613",
                    messages=[
                        {"role": "system", "content": detailed_system_prompt},
                        {"role": "user", "content": user_input}
                    ]
                )
                
                reply = info_response.choices[0].message.content.strip()
                return Response({"type": "info", "reply": reply})

            except Exception as e:
                return Response(
                    {"type": "error", "reply": "Error communicating with GPT."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        else:
            return Response(
                {"type": "error", "reply": "Sorry, I didn't understand your request."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def search_pets(self, filters):
        """
        Search pets based on provided filters.
        
        Args:
            filters (dict): Dictionary containing search criteria
            
        Returns:
            QuerySet: Filtered pet queryset
        """
        qs = Pet.objects.filter()

        # Map textual filters to database values
        status_map = {"lost": 1, "found": 2, "seen": 3}
        species_map = {"dog": 1, "cat": 2, "other": 3}
        size_map = {"small": 1, "medium": 2, "large": 3}
        color_map = {name.lower(): id for id, name in Pet.COLOR_CHOICES}

        # Apply filters
        if "status" in filters:
            status_val = status_map.get(filters["status"].lower())
            if status_val:
                qs = qs.filter(status=status_val)
                
        if "species" in filters:
            species_val = species_map.get(filters["species"].lower())
            if species_val:
                qs = qs.filter(species=species_val)
                
        if "size" in filters:
            size_val = size_map.get(filters["size"].lower())
            if size_val:
                qs = qs.filter(size=size_val)
                
        if "color" in filters:
            color_val = color_map.get(filters["color"].lower())
            if color_val:
                qs = qs.filter(primary_color=color_val)
                
        if "recent_days" in filters:
            try:
                days = int(filters["recent_days"])
                since = now() - timedelta(days=days)
                qs = qs.filter(created_at__gte=since)
            except (ValueError, TypeError):
                pass

        return qs.order_by("-created_at")[:3]


# ============================================================================
# PET RECOMMENDATION API VIEW
# ============================================================================

# Predefined scoring logic for pet recommendations
QUESTIONS = [
    {
        "question": "Cik daudz vietas tev ir mājdzīvniekam?",
        "options": [
            {"answer": "Mazs dzīvoklis", "scores": {"cat": 2, "dog": -1}},
            {"answer": "Vidēja izmēra māja", "scores": {"cat": 1, "dog": 1}},
            {"answer": "Liela māja ar pagalmu", "scores": {"dog": 2, "cat": 0}},
        ],
    },
    # Add more questions as needed
]


class PetRecommendationAPIView(APIView):
    """
    AI-powered pet recommendation system based on user preferences.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Generate pet recommendations based on user answers to lifestyle questions.
        """
        user_answers = request.data.get('answers', [])
        if not user_answers:
            return Response(
                {"error": "No answers provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate scores based on user responses
        scores = {"dog": 0, "cat": 0, "none": 0}
        for answer in user_answers:
            for question in QUESTIONS:
                for option in question["options"]:
                    if option["answer"] == answer:
                        for pet, score in option["scores"].items():
                            scores[pet] += score

        # Determine the best pet choice
        best_pet = max(scores, key=scores.get)

        try:
            # Generate detailed recommendation using OpenAI
            system_message = (
                f"You are an expert in pet recommendations. "
                f"Based on the user's responses, they are best suited for a {best_pet}. "
                f"Please generate a detailed response in the following exact JSON format:\n"
                f"{{\n"
                f"  \"pet\": {{\n"
                f"    \"type\": \"{best_pet}\",\n"
                f"    \"description\": \"A detailed description of the pet, including their general temperament, intelligence, and adaptability. Include specific breed examples that would be suitable.\",\n"
                f"    \"characteristics\": {{\n"
                f"      \"size\": \"Detailed description of size variations, including specific breed examples for each size category (small, medium, large).\",\n"
                f"      \"energy level\": \"Comprehensive description of energy levels, including specific breed examples for each energy level (low, moderate, high).\",\n"
                f"      \"social behavior\": \"Detailed explanation of social behaviors, including specific breed examples that are known for their social traits.\"\n"
                f"    }},\n"
                f"    \"likes\": {{\n"
                f"      \"general\": \"Detailed list of what these pets generally enjoy, including specific activities, toys, and interactions. Include breed-specific examples where relevant.\"\n"
                f"    }},\n"
                f"    \"dislikes\": {{\n"
                f"      \"general\": \"Comprehensive list of what these pets generally dislike, including specific situations, environments, and interactions. Include breed-specific examples where relevant.\"\n"
                f"    }},\n"
                f"    \"whyThisPet\": \"Detailed explanation of why this pet type is a good match for the user, including specific breed recommendations based on their lifestyle and preferences.\"\n"
                f"  }}\n"
                f"}}\n"
                f"Ensure all descriptions are detailed and include specific breed examples. Keep the tone informative yet engaging. "
                f"Focus on providing practical, real-world information that will help the user make an informed decision."
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": system_message}]
            )

            # Extract and parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            try:
                parsed_response = json.loads(ai_response)
                response_data = {"pet": parsed_response["pet"]}
                
                return JsonResponse(response_data, status=status.HTTP_200_OK)
                
            except json.JSONDecodeError:
                return JsonResponse(
                    {"error": "Failed to parse AI response"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {"error": "Failed to generate recommendation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )