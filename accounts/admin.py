from django.urls import path
from . import views

urlpatterns = [
    # Pets owned by the authenticated user
    path('user-pets/', views.UserPetsView.as_view(), name='user_pets'),
    path('user-pets/<int:pet_id>/delete/', views.DeletePetView.as_view(), name='delete_pet'),
    # Services owned by the authenticated user
    path('user-services/', views.UserServicesView.as_view(), name='user_services'),
    path('user-services/<int:service_id>/delete/', views.DeleteServiceView.as_view(), name='delete_service'),

    # Favorite pets - Adding and removing from the pet details page
    path('favorite-pets/<int:pet_id>/', views.FavoritePetView.as_view(), name='favorite_pet'),
    # Favorite services - Adding and removing from the pet details page
    path('favorite-services/<int:service_id>/', views.FavoriteServiceView.as_view(), name='favorite_service'),

    # Getting and removing favorites from user profile
    path('favorite-pets/', views.GetFavoritedPets.as_view(), name='get_favorited_pets'),  # GET all favorited pets
    path('favorite-pets/<int:pet_id>/remove/', views.UnfavoritePetView.as_view(), name='unfavorite_pet'),  # DELETE

    # Getting and removing favorites from user profile
    path('favorite-services/', views.GetFavoritedServices.as_view(), name='get_favorited_services'),  # GET all favorited services
    path('favorite-services/<int:service_id>/remove/', views.UnfavoriteServiceView.as_view(), name='unfavorite_service'),  # DELETE
    
]