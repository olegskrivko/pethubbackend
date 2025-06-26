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


class ChatBotAPIView(APIView):
    #throttle_classes = [UserRateThrottle, AnonRateThrottle]
    def post(self, request):
        user_input = request.data.get("message", "")
        print("User input:", user_input)

        # Step 1: Classification system prompt to extract intent and filters as JSON
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
            print("GPT classification response:", classification_response)

            gpt_content = classification_response.choices[0].message.content
            gpt_result = json.loads(gpt_content)
            print("Parsed GPT result:", gpt_result)
        except Exception as e:
            print("Error during GPT classification or JSON parsing:", e)
            return Response({"type": "error", "reply": "GPT classification error."}, status=500)

        # Step 2: Handle 'search' intent - filter pets from DB
        if gpt_result.get("intent") == "search":
            pets = self.search_pets(gpt_result)
            print("Pets found (queryset):", pets)

            if pets.exists():
                results = [
                    {   "status": pet.status,  # integer
                        "status_display": pet.get_status_display(),  # string, Django model method
                        "species": pet.species,
                        "species_display": pet.get_species_display(),
                        "name": pet.name or "Bezvārda dzīvnieks",
                        "image": pet.pet_image_1,
                        "url": f"/pets/{pet.id}"
                    }
                    for pet in pets
                ]
                print("Formatted pet results:", results)
                return Response({"type": "pet_results", "pets": results})

            else:
                print("No pets matched the filters.")
                return Response({"type": "pet_results", "pets": [], "message": "Nekas netika atrasts."})

        # Step 3: For informational questions, generate an answer with context prompt
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
                print("Informational GPT response:", info_response)
                reply = info_response.choices[0].message.content.strip()
                return Response({"type": "info", "reply": reply})

            except Exception as e:
                print("Error during GPT informational response:", e)
                return Response({"type": "error", "reply": "Error communicating with GPT."}, status=500)

        else:
            # Unknown intent fallback
            return Response({"type": "error", "reply": "Sorry, I didn't understand your request."}, status=400)
    
    def search_pets(self, filters):
        print("Applying filters:", filters)

        # qs = Pet.objects.filter(is_public=True, is_verified=True)
        qs = Pet.objects.filter()
        print("Initial queryset count:", qs.count())

        # Map textual filters to DB values
        status_map = {"lost": 1, "found": 2, "seen": 3}
        species_map = {"dog": 1, "cat": 2, "other": 3}
        size_map = {"small": 1, "medium": 2, "large": 3}
        
        color_map = {name.lower(): id for id, name in Pet.COLOR_CHOICES}
        #color_map = {"brown": 7, "black": 1, "white": 3}  # Extend as needed

        if "status" in filters:
            status_val = status_map.get(filters["status"].lower())
            if status_val:
                qs = qs.filter(status=status_val)
                print("Filtered by status:", filters["status"])
        if "species" in filters:
            species_val = species_map.get(filters["species"].lower())
            if species_val:
                qs = qs.filter(species=species_val)
                print("Filtered by species:", filters["species"])
        if "size" in filters:
            size_val = size_map.get(filters["size"].lower())
            if size_val:
                qs = qs.filter(size=size_val)
                print("Filtered by size:", filters["size"])
        if "color" in filters:
            color_val = color_map.get(filters["color"].lower())
            if color_val:
                qs = qs.filter(primary_color=color_val)
                print("Filtered by color:", filters["color"])
        if "recent_days" in filters:
            try:
                days = int(filters["recent_days"])
                since = now() - timedelta(days=days)
                qs = qs.filter(created_at__gte=since)
                print("Filtered by recent_days:", days)
            except Exception as e:
                print("Invalid recent_days value:", e)

        final_qs = qs.order_by("-created_at")[:3]
        print("Final queryset count:", final_qs.count())
        return final_qs
# class ChatBotAPIView(APIView):
#     def post(self, request):
#         user_input = request.data.get("message", "")
#         print("User input:", user_input)

#         system_prompt = """
# You are an assistant for a lost pet search website. Classify the message as either:
# - "informational": user is asking general questions about pets or lost/found process.
# - "search": user wants to search for pets using filters.

# If it's a search, extract a JSON like:
# {
#   "intent": "search",
#   "status": "lost",
#   "species": "dog",
#   "size": "small",
#   "color": "brown",
#   "recent_days": 7
# }

# Supported filters: status, species, size, color, recent_days
# Status: lost, found, seen
# Species: dog, cat, other
# Size: small, medium, large
# Color: black, white, brown, etc.

# If it's not a search, return:
# { "intent": "informational" }
# """

#         # Step 1: Ask GPT to classify and extract filters using new client method
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4",
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_input}
#                 ]
#             )
#             print("GPT filter classification response:", response)
#             gpt_content = response.choices[0].message.content
#             gpt_result = json.loads(gpt_content)
#             print("Parsed GPT result:", gpt_result)
#         except Exception as e:
#             print("Error during GPT classification or parsing:", e)
#             return Response({"type": "error", "reply": "GPT klasifikācijas kļūda."}, status=500)

#         # Step 2: Handle intent
#         if gpt_result.get("intent") == "search":
#             pets = self.search_pets(gpt_result)
#             print("Pets found (queryset):", pets)

#             if pets:
#                 results = [
#                     {
#                         "name": pet.name or "Bezvārda dzīvnieks",
#                         "image": pet.pet_image_1,
#                         "url": f"/pets/{pet.id}"
#                     }
#                     for pet in pets
#                 ]
#                 print("Formatted pet results:", results)
#                 return Response({"type": "pet_results", "pets": results})
#             else:
#                 print("No pets matched the filters.")
#                 return Response({"type": "pet_results", "pets": [], "message": "Nekas netika atrasts."})
#         else:
#             # For informational questions, get GPT answer again
#             try:
#                 info_response = client.chat.completions.create(
#                     model="gpt-4",
#                     messages=[
#                         {"role": "system", "content": "You are a friendly assistant for a lost pet website."},
#                         {"role": "user", "content": user_input}
#                     ]
#                 )
#                 print("Informational GPT response:", info_response)
#                 reply = info_response.choices[0].message.content
#                 return Response({"type": "info", "reply": reply})
#             except Exception as e:
#                 print("Error during GPT informational response:", e)
#                 return Response({"type": "error", "reply": "Kļūda saziņā ar GPT."}, status=500)

#     def search_pets(self, filters):
#         print("Applying filters:", filters)

#         qs = Pet.objects.filter(is_public=True, is_verified=True)
#         print("Initial queryset count:", qs.count())

#         status_map = {"lost": 1, "found": 2, "seen": 3}
#         species_map = {"dog": 1, "cat": 2, "other": 3}
#         size_map = {"small": 1, "medium": 2, "large": 3}
#         color_map = {"brown": 7, "black": 1, "white": 3}  # Add more if needed

#         if "status" in filters:
#             qs = qs.filter(status=status_map.get(filters["status"], 1))
#             print("Filtered by status:", filters["status"])
#         if "species" in filters:
#             qs = qs.filter(species=species_map.get(filters["species"], 1))
#             print("Filtered by species:", filters["species"])
#         if "size" in filters:
#             qs = qs.filter(size=size_map.get(filters["size"], 1))
#             print("Filtered by size:", filters["size"])
#         if "color" in filters:
#             qs = qs.filter(primary_color=color_map.get(filters["color"], 7))
#             print("Filtered by color:", filters["color"])
#         if "recent_days" in filters:
#             since = now() - timedelta(days=filters["recent_days"])
#             qs = qs.filter(created_at__gte=since)
#             print("Filtered by recent_days:", filters["recent_days"])

#         final_qs = qs.order_by("-created_at")[:5]
#         print("Final queryset count:", final_qs.count())
#         return final_qs
# class ChatBotAPIView(APIView):
#     permission_classes = [IsAuthenticated]  # Only authenticated users can use the chatbot
    
#     def post(self, request, *args, **kwargs):
#         """
#         Accepts a message from the user and returns a response generated by OpenAI,
#         but only answers questions relevant to dogs, cats, and related topics.
#         """
        
#         user_message = request.data.get('message', None)
#         if not user_message:
#             return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

#         # Debugging: Print the incoming user message
#         print(f"Received user message: {user_message}")

#         try:
#             # Define the system message to make the chatbot focus on dogs and cats
#             system_message = (
#                 "You are an expert cynologist and veterinarian specializing in dogs and cats. "
#                 "Your job is to provide helpful, accurate, and relevant information about dogs and cats only. "
#                 "You are not allowed to provide responses unrelated to dogs, cats, or any pets similar to them. "
#                 "Your answers should include guidance on care, training, adoption, health issues, finding lost pets, etc. "
#                 "Focus on providing the essential information only. "
#                 "Avoid long explanations, and limit responses to a few sentences. "
#                 "No unnecessary elaboration or details. Only what's necessary to answer the user's question. "
#                 "If the question requires multiple steps, summarize the steps in short bullet points. "
#                 # "Please be detailed and professional in your responses."
                
#             )

#             # Combine the system prompt with the user's message to ensure focus
#             conversation = [
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": user_message}
#             ]

#             # Debugging: Print the conversation being sent to OpenAI
#             print(f"Sending the following conversation to OpenAI: {conversation}")

#             # Generate AI response
#             response = client.chat.completions.create(
#                 model="gpt-4",  # You can use "gpt-3.5-turbo" if you prefer a smaller model
#                 messages=conversation
#             )

#             # Debugging: Print the raw response from OpenAI
#             print(f"Raw response from OpenAI: {response}")

#             # Extract the AI's response
#             ai_response = response.choices[0].message.content.strip()

#             # Debugging: Print the AI's response
#             print(f"AI response: {ai_response}")

#             # Return the AI's response as a JSON response
#             return Response({"response": ai_response}, status=status.HTTP_200_OK)

#         except Exception as e:
#             # Debugging: Print the error message
#             print(f"Error occurred: {str(e)}")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Predefined scoring logic
QUESTIONS = [
    {
        "question": "Cik daudz vietas tev ir mājdzīvniekam?",
        "options": [
            {"answer": "Mazs dzīvoklis", "scores": {"cat": 2, "dog": -1}},
            {"answer": "Vidēja izmēra māja", "scores": {"cat": 1, "dog": 1}},
            {"answer": "Liela māja ar pagalmu", "scores": {"dog": 2, "cat": 0}},
        ],
    },
    # Add more questions...
]

class PetRecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    

    def post(self, request, *args, **kwargs):
        print("=== Debug Authentication ===")
        print("Auth header:", request.headers.get('Authorization'))
        print("User:", request.user)
        print("User is authenticated:", request.user.is_authenticated)
        print("Request headers:", dict(request.headers))
        print("=========================")
        
        user_answers = request.data.get('answers', [])
        if not user_answers:
            return Response(
                {"error": "No answers provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        scores = {"dog": 0, "cat": 0, "none": 0}

        # Calculate scores based on user responses
        for answer in user_answers:
            for question in QUESTIONS:
                for option in question["options"]:
                    if option["answer"] == answer:
                        for pet, score in option["scores"].items():
                            scores[pet] += score

        # Determine the best pet choice
        best_pet = max(scores, key=scores.get)

        try:
            # Generate response using OpenAI
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

            conversation = [
                {"role": "system", "content": system_message}
            ]

            print("=== Debug OpenAI Request ===")
            print("System message:", system_message)
            print("=========================")

            response = client.chat.completions.create(
                model="gpt-4",
                messages=conversation
            )

            # Extract AI-generated content
            ai_response = response.choices[0].message.content.strip()
            
            print("=== Debug OpenAI Response ===")
            print("Raw AI response:", ai_response)
            print("=========================")

            try:
                # Parse the AI response into a Python dictionary
                parsed_response = json.loads(ai_response)
                print("=== Debug Parsed Response ===")
                print("Parsed JSON:", parsed_response)
                print("=========================")

                # Create the response data
                response_data = {"pet": parsed_response["pet"]}
                print("=== Debug Final Response ===")
                print("Response being sent:", response_data)
                print("Response type:", type(response_data))
                print("=========================")

                # Return the pet data directly
                return JsonResponse(
                    response_data,
                    status=status.HTTP_200_OK
                )
            except json.JSONDecodeError as e:
                print("=== Debug JSON Error ===")
                print("Error parsing JSON:", str(e))
                print("Raw response:", ai_response)
                print("=========================")
                return JsonResponse(
                    {"error": "Failed to parse AI response"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            print(f"Error in OpenAI call: {str(e)}")  # Debug print
            return Response(
                {"error": "Failed to generate recommendation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )