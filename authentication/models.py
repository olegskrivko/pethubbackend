from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
from .utils import generate_uuid_username

class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle user creation with email as the unique identifier 
    and automatic generation of username and avatar.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        Automatically generates a unique username and avatar.

        Args:
            email (str): User's email address.
            password (str, optional): User's password.
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If email is not provided.

        Returns:
            CustomUser: Newly created user instance.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)

        username, avatar = generate_uuid_username()
        extra_fields['username'] = username
        extra_fields['avatar'] = avatar
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        Automatically verifies and activates the superuser,
        and generates username and avatar.

        Args:
            email (str): Superuser's email address.
            password (str, optional): Superuser's password.
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If is_staff or is_superuser flags are not set to True.

        Returns:
            CustomUser: Newly created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Automatically verify superuser
        extra_fields.setdefault('is_verified', True) 
        # Automatically activate superuser
        extra_fields.setdefault('is_active', True) 
        # Enforce correct flag values explicitly
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        # Always auto-generate superuser username
        username, avatar = generate_uuid_username()
        extra_fields['username'] = username
        extra_fields['avatar'] = avatar
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Uses email as the USERNAME_FIELD and auto-generates username and avatar.
    Supports email verification and password reset tokens.
    """
    username = models.CharField(max_length=255, unique=True, blank=True)
    email = models.EmailField(unique=True)

    # Auth & Verification
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=100, blank=True, null=True)
    activation_token_expires = models.DateTimeField(blank=True, null=True)

    # Password Reset
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)

    # Avatar animal
    avatar = models.CharField(max_length=100, blank=True, null=True)

    # Permissions
    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # username is auto-generated, so we don't require it

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """Generate activation token and expiry date only on user creation."""
        if not self.pk: # Only generate token when user is first created
            self.activation_token = str(uuid.uuid4())
            self.activation_token_expires = timezone.now() + timedelta(hours=24)

            if not self.username:
                username, avatar = generate_uuid_username()
                self.username = username
                self.avatar = avatar

        super().save(*args, **kwargs)

    def generate_password_reset_token(self):
        """
        Generate a new password reset token and set its expiry time to 1 hour from now.
        Saves the user instance after updating the token and expiry fields.
        """
        self.password_reset_token = str(uuid.uuid4())
        self.password_reset_expires = timezone.now() + timedelta(hours=1)
        self.save()

    def clear_password_reset_token(self):
        """
        Clear the password reset token and its expiry time.
        Saves the user instance after clearing these fields.
        """
        self.password_reset_token = None
        self.password_reset_expires = None
        self.save()

    def __str__(self):
        """
        Return a string representation of the user, which is the user's email.
        """
        return self.email