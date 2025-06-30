from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import status
from django.shortcuts import get_object_or_404

# Import models
from pets.models import Pet, UserFavorites
from services.models import Service, UserServiceFavorites

# Import serializers
from pets.serializers import PetSerializer
from services.serializers import ServiceSerializer


# ============================================================================
# PET MANAGEMENT VIEWS
# ============================================================================

class UserPetsView(APIView):
    """
    View to retrieve all pets owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all pets created by the authenticated user."""
        user = request.user
        pets = Pet.objects.filter(author=user)
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdatePetStatusView(APIView):
    """
    View to update the status of a pet owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pet_id):
        """Update pet status with partial data."""
        try:
            pet = Pet.objects.get(id=pet_id, author=request.user)
        except Pet.DoesNotExist:
            return Response(
                {'error': 'Pet not found or not authorized'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PetSerializer(pet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeletePetView(APIView):
    """
    View to delete a specific pet owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pet_id):
        """Delete a pet if the user is the owner."""
        try:
            pet = Pet.objects.get(id=pet_id, author=request.user)
        except Pet.DoesNotExist:
            raise NotFound(detail="Pet not found or you do not have permission to delete it.")

        pet.delete()
        return Response({"detail": "Pet deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# SERVICE MANAGEMENT VIEWS
# ============================================================================

class UserServicesView(APIView):
    """
    View to retrieve all services owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all services created by the authenticated user."""
        user = request.user
        services = Service.objects.filter(user=user)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteServiceView(APIView):
    """
    View to delete a specific service owned by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, service_id):
        """Delete a service if the user is the owner."""
        try:
            service = Service.objects.get(id=service_id, user=request.user)
        except Service.DoesNotExist:
            raise NotFound(detail="Service not found or you do not have permission to delete it.")

        service.delete()
        return Response({"detail": "Service deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# PET FAVORITES MANAGEMENT
# ============================================================================

class GetFavoritedPets(APIView):
    """
    View to retrieve all pets that the authenticated user has favorited.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all pets that the user has favorited."""
        user = request.user
        favorite_pets = UserFavorites.objects.filter(user=user).select_related('pet')
        pets = [favorite.pet for favorite in favorite_pets]
        serialized_pets = PetSerializer(pets, many=True)
        return Response(serialized_pets.data, status=status.HTTP_200_OK)


class FavoritePetView(APIView):
    """
    View to manage pet favorites (check, add, remove).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pet_id):
        """Check if a pet is in the user's favorites."""
        user = request.user
        pet = get_object_or_404(Pet, id=pet_id)
        is_favorite = UserFavorites.objects.filter(user=user, pet=pet).exists()
        return Response({"is_favorite": is_favorite}, status=status.HTTP_200_OK)

    def post(self, request, pet_id):
        """Add a pet to the user's favorites."""
        user = request.user
        pet = get_object_or_404(Pet, id=pet_id)

        if UserFavorites.objects.filter(user=user, pet=pet).exists():
            return Response(
                {"detail": "Pet is already in favorites."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        UserFavorites.objects.create(user=user, pet=pet)
        return Response({"detail": "Pet added to favorites."}, status=status.HTTP_201_CREATED)

    def delete(self, request, pet_id):
        """Remove a pet from the user's favorites."""
        user = request.user
        pet = get_object_or_404(Pet, id=pet_id)

        favorite = UserFavorites.objects.filter(user=user, pet=pet)
        if not favorite.exists():
            return Response(
                {"detail": "Pet is not in favorites."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        favorite.delete()
        return Response({"detail": "Pet removed from favorites."}, status=status.HTTP_204_NO_CONTENT)


class UnfavoritePetView(APIView):
    """
    View to remove a pet from favorites (alternative endpoint).
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pet_id):
        """Remove a pet from the user's favorites."""
        user = request.user
        favorite_pet = get_object_or_404(UserFavorites, pet_id=pet_id, user=user)
        favorite_pet.delete()
        return Response({"message": "Pet removed from favorites"}, status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# SERVICE FAVORITES MANAGEMENT
# ============================================================================

class GetFavoritedServices(APIView):
    """
    View to retrieve all services that the authenticated user has favorited.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all services that the user has favorited."""
        user = request.user
        favorite_services = UserServiceFavorites.objects.filter(user=user).select_related('service')
        services = [favorite.service for favorite in favorite_services]
        serialized_services = ServiceSerializer(services, many=True)
        return Response(serialized_services.data, status=status.HTTP_200_OK)


class FavoriteServiceView(APIView):
    """
    View to manage service favorites (check, add, remove).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, service_id):
        """Check if a service is in the user's favorites."""
        user = request.user
        service = get_object_or_404(Service, id=service_id)
        is_favorite = UserServiceFavorites.objects.filter(user=user, service=service).exists()
        return Response({"is_favorite": is_favorite}, status=status.HTTP_200_OK)

    def post(self, request, service_id):
        """Add a service to the user's favorites."""
        user = request.user
        service = get_object_or_404(Service, id=service_id)

        if UserServiceFavorites.objects.filter(user=user, service=service).exists():
            return Response(
                {"detail": "Service is already in favorites."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        UserServiceFavorites.objects.create(user=user, service=service)
        return Response({"detail": "Service added to favorites."}, status=status.HTTP_201_CREATED)

    def delete(self, request, service_id):
        """Remove a service from the user's favorites."""
        user = request.user
        service = get_object_or_404(Service, id=service_id)

        favorite = UserServiceFavorites.objects.filter(user=user, service=service)
        if not favorite.exists():
            return Response(
                {"detail": "Service is not in favorites."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        favorite.delete()
        return Response({"detail": "Service removed from favorites."}, status=status.HTTP_204_NO_CONTENT)


class UnfavoriteServiceView(APIView):
    """
    View to remove a service from favorites (alternative endpoint).
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, service_id):
        """Remove a service from the user's favorites."""
        user = request.user
        favorite_service = get_object_or_404(UserServiceFavorites, service_id=service_id, user=user)
        favorite_service.delete()
        return Response({"message": "Service removed from favorites"}, status=status.HTTP_204_NO_CONTENT)