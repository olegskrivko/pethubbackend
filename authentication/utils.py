# \authentication\utils.py
import uuid
import random
from django.contrib.auth import get_user_model

# Pet-themed adjectives and animals
ADJECTIVES = [
    "Happy", "Clever", "Swift", "Brave", "Loyal", "Gentle",
    "Curious", "Playful", "Furry", "Energetic"
]

PET_NAMES = [
    "Fox", "Dog", "Cat", "Bear", "Horse", "Alligator",
    "Penguin", "Pig", "Lion", "Owl"
]

def generate_uuid_username(max_attempts=5):
    """
    Generate a unique pet-themed username with a 6-digit hex suffix.
    Falls back to a generic uuid-based username if all attempts fail.
    """
    User = get_user_model() # moved inside function, to avoid circular import

    for _ in range(max_attempts):
        adjective = random.choice(ADJECTIVES)
        pet = random.choice(PET_NAMES)
        uid = uuid.uuid4().hex[:6].upper() # 6-character hex string
        username = f"{adjective}{pet}_{uid}"

        if not User.objects.filter(username=username).exists():
            return username, pet  # return both username and avatar

    # Fallback if no unique username found in given attempts
    fallback = f"user_{uuid.uuid4().hex[:8]}"
    return fallback, "Cat"  # Default avatar animal

