from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import os
from django.utils.timezone import now
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
#from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited
from django.http import JsonResponse, HttpRequest
from .ratelimit_utils import (
    register_rate_limit,
    login_rate_limit,
    activate_rate_limit,

    default_rate_limit,
    forgot_password_rate_limit,
    test_rate_limit,
)
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import get_user_model
User = get_user_model()

DOMAIN_APP_URL = os.getenv("DOMAIN_APP_URL")

@register_rate_limit
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Handles user registration and sends a verification email."""
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()  # Serializer handles user creation & email sending
        return Response({
            "message": "User registered! Check your email to verify your account."
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@activate_rate_limit
@api_view(["GET"])
@permission_classes([AllowAny])  # ✅ Make activation public
def activate_user(request, token):
    """Activate the user if the token is valid and not expired."""
    user = get_object_or_404(User, activation_token=token)

    # ✅ Check if the account is already active
    if user.is_active:
        return Response({"message": "Account is already verified!"}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Check if the activation token is expired
    if user.activation_token_expires and user.activation_token_expires < now():
        return Response({"error": "Activation link has expired."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Activate the user
    user.is_active = True
    user.is_verified = True  # If you are using a separate `is_verified` field
    user.activation_token = None  # ✅ Remove the token
    user.activation_token_expires = None  # ✅ Clear expiry
    user.save()

    # ✅ Redirect to React frontend login page instead of Django
    return redirect(f"{DOMAIN_APP_URL}/login")  # Change to your React frontend URL
    #return redirect(f"{DOMAIN_APP_URL}/login?activated=true")
    #return Response({"message": "Account activated successfully"}, status=200)

@login_rate_limit
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Handles user login with JWT authentication."""
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]  # Extract user
        refresh = RefreshToken.for_user(user)  # Generate JWT tokens
        access_token = refresh.access_token

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "username": user.username,
            "avatar": user.avatar,
            "id": user.id,
            "expires_in": access_token.lifetime.total_seconds(), 
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def logout(request: HttpRequest):
    return JsonResponse({"message": "Logout view"})

@forgot_password_rate_limit
def password_reset(request: HttpRequest):
    return JsonResponse({"message": "Password reset view"})

def password_reset_confirm(request: HttpRequest):
    return JsonResponse({"message": "Password reset confirm"})

def change_password(request: HttpRequest):
    return JsonResponse({"message": "Change password"})



# DEBUGING
@test_rate_limit
def test_view(request):
    return JsonResponse({"message": "This view is rate limited to 3 requests per minute"})

@test_rate_limit
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_example(request):
    user = request.user
    return Response({
        "message": "This is a protected route.",
        "user_email": user.email,
        "username": user.username
    })

@test_rate_limit
@api_view(["GET"])
@permission_classes([AllowAny])
def public_example(request):
    return Response({
        "message": "This is a public route. No authentication required."
    })

### ✅ Get User Details (Authenticated Users Only)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    """Returns user details for authenticated users."""
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
    }, status=status.HTTP_200_OK)

