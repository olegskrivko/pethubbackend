from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.utils import generate_uuid_username 
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "password", "username"]
        read_only_fields = ["username"]

    def validate_email(self, value):
        """Ensure email is unique before creating the user."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        """Create a user with a unique username and send a verification email."""
        email = validated_data["email"]
        password = validated_data["password"]

        # Generate unique username and avatar (from your helper)
        username, avatar = generate_uuid_username()

        try:
            with transaction.atomic(): # Ensures user is fully saved or rolled back
                user = User(
                    email=email,
                    username=username,
                    avatar=avatar, # Save the animal for the avatar
                    is_active=False  # Prevent login until verified
                )
                user.set_password(password)
                user.save()
                self.send_verification_email(user)
                return user

        except Exception as e:
            raise serializers.ValidationError("Something went wrong. Please try again.")

    def send_verification_email(self, user):
        """Send email with activation link using HTML template."""
        activation_url = f"{settings.API_BASE_URL}/api/auth/activate/{user.activation_token}/"

        subject = "Verify Your Email"
        html_message = render_to_string("emails/email_verification.html", {"activation_url": activation_url})
        print(subject, html_message, user.email, settings.EMAIL_HOST_USER )
        send_mail(
            subject,
            message="",  # Empty text message, only sending HTML
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_message,)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate email & password for authentication"""
        email = data.get("email")
        password = data.get("password")

        # Authenticate with email
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError({"detail": "Invalid email or password"})
        if not user.is_active:
            raise serializers.ValidationError({"detail": "Account is inactive. Please verify your email."})
        return {"user": user}


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    user = None  # Hold the user here

    def validate_email(self, value):
        """Check if user exists and is active."""
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive. Please contact support.")
        
        self.user = user  # Save the user for use in save()
        return value

    def save(self):
        """Generate reset token and send email."""
        user = self.user  # Reuse validated user
        #email = self.validated_data["email"]
        #user = User.objects.get(email=email)
        
        user.generate_password_reset_token()  # Calls model method
        
        reset_url = f"{settings.API_BASE_URL}/api/auth/reset-password/{user.password_reset_token}/"
        subject = "Reset Your Password"
        message = f"Click the link below to reset your password:\n\n{reset_url}"
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

        return {"message": "Password reset email sent!"}

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    token = serializers.CharField()

    def validate(self, data):
        """Check if token is valid and not expired."""
        try:
            user = User.objects.get(password_reset_token=data["token"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token.")

        if user.password_reset_expires and user.password_reset_expires < now():
            raise serializers.ValidationError("Password reset link has expired.")

        data["user"] = user  # ✅ Pass user instance to `save()`
        return data

    def save(self):
        """Set new password and clear reset token."""
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()

        return user  # ✅ Return updated user


