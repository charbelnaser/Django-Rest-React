from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timezone, timedelta
import json


class User(AbstractUser):
    """Extended User model with additional fields for Movies Vault - MongoDB Compatible"""

    class UserRole(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        VIEWER = "viewer", "Viewer"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.VIEWER
    )
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    favorite_genres = models.TextField(blank=True, default="[]")  # Store as JSON string
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the login field.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "auth_user"  # Keep same table name for compatibility

    def __str__(self):
        return self.username

    def get_favorite_genres(self):
        """Get favorite genres as a list"""
        try:
            return json.loads(self.favorite_genres) if self.favorite_genres else []
        except json.JSONDecodeError:
            return []

    def set_favorite_genres(self, genres_list):
        """Set favorite genres from a list"""
        self.favorite_genres = json.dumps(genres_list)


class UserPreferences(models.Model):
    """User preferences for movie recommendations - MongoDB Compatible"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )
    preferred_genres = models.TextField(
        blank=True, default="[]"
    )  # Store as JSON string
    preferred_languages = models.TextField(
        blank=True, default="[]"
    )  # Store as JSON string
    min_rating = models.FloatField(default=6.0)
    include_adult = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_preferences"

    def __str__(self):
        return f"{self.user.username} - Preferences"

    def get_preferred_genres(self):
        """Get preferred genres as a list"""
        try:
            return json.loads(self.preferred_genres) if self.preferred_genres else []
        except json.JSONDecodeError:
            return []

    def set_preferred_genres(self, genres_list):
        """Set preferred genres from a list"""
        self.preferred_genres = json.dumps(genres_list)

    def get_preferred_languages(self):
        """Get preferred languages as a list"""
        try:
            return (
                json.loads(self.preferred_languages) if self.preferred_languages else []
            )
        except json.JSONDecodeError:
            return []

    def set_preferred_languages(self, languages_list):
        """Set preferred languages from a list"""
        self.preferred_languages = json.dumps(languages_list)


class BlacklistedToken(models.Model):
    """
    Simple model to store blacklisted JWT tokens - MongoDB Compatible
    """

    token = models.TextField(unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "blacklisted_tokens"
        ordering = ["-blacklisted_at"]

    def __str__(self):
        return f"Blacklisted token: {self.token[:20]}..."

    @classmethod
    def is_blacklisted(cls, token):
        """Check if a token is blacklisted"""
        return cls.objects.filter(token=token).exists()

    @classmethod
    def blacklist_token(cls, token, expires_at=None):
        """Add a token to the blacklist"""
        if expires_at is None:
            # Default to 7 days from now
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        obj, created = cls.objects.get_or_create(
            token=token, defaults={"expires_at": expires_at}
        )
        return obj, created

    @classmethod
    def cleanup_expired(cls):
        """Remove expired tokens from blacklist"""
        now = datetime.now(timezone.utc)
        expired_count = cls.objects.filter(expires_at__lt=now).delete()[0]
        return expired_count
