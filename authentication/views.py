from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import os
import uuid
from django.conf import settings

from django.core.mail import EmailMultiAlternatives, send_mail
from datetime import datetime, timedelta
from django.utils.timezone import now
from .serializers import RegisterSerializer, LoginSerializer, ResetPasswordSerializer, ForgotPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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



# def logout(request: HttpRequest):
#     return JsonResponse({"message": "Logout view"})

# @forgot_password_rate_limit
# def password_reset(request: HttpRequest):
#     return JsonResponse({"message": "Password reset view"})
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request, token):  # ✅ Token must match URLs
    print("token", token)
    """Handles password reset using a valid token."""
    try:
        user = User.objects.get(password_reset_token=token)
    except User.DoesNotExist:
        return Response({"error": "Invalid or expired token."}, status=400)

    # ✅ Check if token is expired
    if user.password_reset_expires and user.password_reset_expires < now():
        return Response({"error": "Password reset link has expired."}, status=400)

    # ✅ Update password
    new_password = request.data.get("password")
    if not new_password:
        return Response({"error": "Password is required."}, status=400)

    user.set_password(new_password)
    user.password_reset_token = None  # ✅ Remove token after use
    user.password_reset_expires = None
    user.save()

    return Response(
        {"message": "Password reset successfully! You can now log in."}, status=200
    )
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request, token):
    """Handles password reset using a valid token."""
    data = request.data.copy()  # ✅ Copy request data
    data["token"] = token  # ✅ Add `token` from URL to data

    serializer = ResetPasswordSerializer(data=data)
    if serializer.is_valid():
        serializer.save()  # ✅ Calls `save()` and updates password
        return Response(
            {"message": "Password reset successfully! You can now log in."}, status=200
        )

    return Response(serializer.errors, status=400)  # 🚨 Send back validation errors
# def password_reset_confirm(request: HttpRequest):
#     return JsonResponse({"message": "Password reset confirm"})

# def change_password(request: HttpRequest):
#     return JsonResponse({"message": "Change password"})

@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    """Handles password reset requests by sending an email."""
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "No account found with this email."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # ✅ Generate password reset token
    user.password_reset_token = str(uuid.uuid4())
    user.password_reset_expires = now() + timedelta(hours=1)  # Token expires in 1 hour
    user.save()

    # ✅ Create the reset link
    reset_url = f"{DOMAIN_APP_URL}/reset-password/{user.password_reset_token}/"

    # ✅ Render HTML email template
    context = {"reset_url": reset_url, "user": user}
    html_content = render_to_string(
        "emails/reset_password.html", context
    )  # Load email template
    plain_text_content = strip_tags(html_content)  # Convert HTML to plain text

    # ✅ Send email
    subject = "Reset Your Password"
    email_message = EmailMultiAlternatives(
        subject, plain_text_content, settings.EMAIL_HOST_USER, [user.email]
    )
    email_message.attach_alternative(html_content, "text/html")  # Attach HTML version
    email_message.send()

    return Response(
        {"message": "Password reset email sent!"}, status=status.HTTP_200_OK
    )

# DEBUGING
# @test_rate_limit
# def test_view(request):
#     return JsonResponse({"message": "This view is rate limited to 3 requests per minute"})

# @test_rate_limit
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def protected_example(request):
#     user = request.user
#     return Response({
#         "message": "This is a protected route.",
#         "user_email": user.email,
#         "username": user.username
#     })

# @test_rate_limit
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def public_example(request):
#     return Response({
#         "message": "This is a public route. No authentication required."
#     })

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



### ✅ Delete User View (Soft Delete Instead of Permanent Deletion)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """Soft deletes the user account (deactivates it)."""
    user = request.user
    user.is_active = False  # ✅ Instead of deleting, deactivate the account
    user.save()
    return Response(
        {"message": "User account deactivated successfully."},
        status=status.HTTP_204_NO_CONTENT,
    )


### ✅ Logout View (Blacklist Token)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Handles logout by blacklisting refresh token."""
    if "refresh" not in request.data:
        return Response(
            {"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()  # ✅ Blacklist the token
        return Response(
            {"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT
        )
    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)