from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.text import slugify
from .models import User, UserPreferences


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "first_name",
            "last_name",
            "date_of_birth",
            "profile_picture",
            "bio",
            "favorite_genres",
            "date_joined",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "date_joined", "created_at", "updated_at")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        email = validated_data["email"].strip().lower()
        password = validated_data.pop("password")
        base_username = slugify(email.split("@")[0]) or "user"
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=User.UserRole.VIEWER,
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            attrs["user"] = user
        else:
            raise serializers.ValidationError("Must include email and password")
        return attrs


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = (
            "preferred_genres",
            "preferred_languages",
            "min_rating",
            "include_adult",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")
