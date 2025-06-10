from rest_framework.views import APIView
from pets.serializers import PetSerializer
from services.serializers import ServiceSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from pets.models import Pet
from services.models import Service

from pets.models import UserFavorites
from services.models import UserServiceFavorites

from django.shortcuts import get_object_or_404

# View to get pets owned by the authenticated user
class UserPetsView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        user = request.user  # Get the logged-in user
        pets = Pet.objects.filter(author=user)  # Fetch pets created by this user
        
        # Serialize the pets data
        serializer = PetSerializer(pets, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserServicesView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        user = request.user  # Get the logged-in user
        services = Service.objects.filter(user=user)  # Fetch services created by this user
        
        # Serialize the services data
        serializer = ServiceSerializer(services, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

# View to delete a specific pet owned by the authenticated user
class DeletePetView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def delete(self, request, pet_id):
        try:
            pet = Pet.objects.get(id=pet_id, author=request.user)  # Fetch pet by id and ensure the user is the owner
        except Pet.DoesNotExist:
            raise NotFound(detail="Pet not found or you do not have permission to delete it.")

        pet.delete()  # Delete the pet
        return Response({"detail": "Pet deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
# View to delete a specific service owned by the authenticated user
class DeleteServiceView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def delete(self, request, service_id):
        try:
            service = Service.objects.get(id=service_id, user=request.user)  # Fetch service by id and ensure the user is the owner
        except Service.DoesNotExist:
            raise NotFound(detail="Service not found or you do not have permission to delete it.")

        service.delete()  # Delete the service
        return Response({"detail": "Service deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class GetFavoritedPets(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all pets that the user has favorited
        favorite_pets = UserFavorites.objects.filter(user=user).select_related('pet')

        # Serialize the pet data
        pets = [favorite.pet for favorite in favorite_pets]
        serialized_pets = PetSerializer(pets, many=True)

        return Response(serialized_pets.data, status=status.HTTP_200_OK)
    
class GetFavoritedServices(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all services that the user has favorited
        favorite_services = UserServiceFavorites.objects.filter(user=user).select_related('service')

        # Serialize the service data
        services = [favorite.service for favorite in favorite_services]
        serialized_services = ServiceSerializer(services, many=True)

        return Response(serialized_services.data, status=status.HTTP_200_OK)


class FavoritePetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pet_id):
        """Check if a pet is in the user's favorites."""
        user = request.user
        pet = get_object_or_404(Pet, id=pet_id)

        # Check if the pet is favorited
        is_favorite = UserFavorites.objects.filter(user=user, pet=pet).exists()
        return Response({"is_favorite": is_favorite}, status=status.HTTP_200_OK)

    def post(self, request, pet_id):
        """Add a pet to the user's favorites."""
        user = request.user
        pet = get_object_or_404(Pet, id=pet_id)

        # Check if already favorited
        if UserFavorites.objects.filter(user=user, pet=pet).exists():
            return Response({"detail": "Pet is already in favorites."}, status=status.HTTP_400_BAD_REQUEST)

        # Add to favorites
        UserFavorites.objects.create(user=user, pet=pet)
        return Response({"detail": "Pet added to favorites."}, status=status.HTTP_201_CREATED)

    def delete(self, request, pet_id):
        """Remove a pet from the user's favorites."""
        user = request.user
        pet = get_object_or_404(Pet, id=pet_id)

        # Check if pet is in favorites
        favorite = UserFavorites.objects.filter(user=user, pet=pet)
        if not favorite.exists():
            return Response({"detail": "Pet is not in favorites."}, status=status.HTTP_404_NOT_FOUND)

        # Remove from favorites
        favorite.delete()
        return Response({"detail": "Pet removed from favorites."}, status=status.HTTP_204_NO_CONTENT)
    

class FavoriteServiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, service_id):
        """Check if a service is in the user's favorites."""
        user = request.user
        service = get_object_or_404(Service, id=service_id)

        # Check if the service is favorited
        is_favorite = UserServiceFavorites.objects.filter(user=user, service=service).exists()
        return Response({"is_favorite": is_favorite}, status=status.HTTP_200_OK)

    def post(self, request, service_id):
        """Add a service to the user's favorites."""
        user = request.user
        service = get_object_or_404(Service, id=service_id)

        # Check if already favorited
        if UserServiceFavorites.objects.filter(user=user, service=service).exists():
            return Response({"detail": "Service is already in favorites."}, status=status.HTTP_400_BAD_REQUEST)

        # Add to favorites
        UserServiceFavorites.objects.create(user=user, service=service)
        return Response({"detail": "Service added to favorites."}, status=status.HTTP_201_CREATED)

    def delete(self, request, service_id):
        """Remove a service from the user's favorites."""
        user = request.user
        service = get_object_or_404(Service, id=service_id)

        # Check if service is in favorites
        favorite = UserServiceFavorites.objects.filter(user=user, service=service)
        if not favorite.exists():
            return Response({"detail": "Service is not in favorites."}, status=status.HTTP_404_NOT_FOUND)

        # Remove from favorites
        favorite.delete()
        return Response({"detail": "Service removed from favorites."}, status=status.HTTP_204_NO_CONTENT)
# View to remove a favorited pet
class UnfavoritePetView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pet_id):
        user = request.user
        favorite_pet = get_object_or_404(UserFavorites, pet_id=pet_id, user=user)
        favorite_pet.delete()
        return Response({"message": "Pet removed from favorites"}, status=status.HTTP_204_NO_CONTENT)
    
# View to remove a favorited service
class UnfavoriteServiceView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, service_id):
        user = request.user
        favorite_service = get_object_or_404(UserServiceFavorites, service_id=service_id, user=user)
        favorite_service.delete()
        return Response({"message": "Service removed from favorites"}, status=status.HTTP_204_NO_CONTENT)