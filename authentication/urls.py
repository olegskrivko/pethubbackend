from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import register, activate_user, login, logout, password_reset, password_reset_confirm, change_password, protected_example, public_example

urlpatterns = [
    # Register a new user and send activation email
    path('register/', register, name='register'),
    # Activate user account via token (from email)
    path('activate/<str:token>/', activate_user, name='activate'),
    # Log in with email/username and password, return JWT
    path('login/', login, name='login'),
    # Log out user, invalidate token if necessary
    path('logout/', logout, name='logout'),
    # Refresh access token using a refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Send reset link to user's email
    path('password-reset/', password_reset, name='password_reset'),
    # Reset password using the link token
    path('password-reset/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
     # Authenticated user changes password manually
    path('password-change/', change_password, name='password_change'),
    

    path('user/', views.get_user_details, name='user-details'),  # ✅ New endpoint
    #path('reset-password-confirm/<uidb64>/<token>/', reset_password_confirm, name='reset-password-confirm'),
    path('test-rate-limit/', views.test_view, name='test-rate-limit'),
    path('protected/', protected_example, name='protected_example'),
    path('public/', public_example, name='public_example'),
    
] 


