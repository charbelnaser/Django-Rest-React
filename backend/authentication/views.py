from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from .models import User, UserPreferences
from .permissions import IsAdmin
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserPreferencesSerializer,
)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No user with this email."}, status=status.HTTP_404_NOT_FOUND
            )
        # Generate a token and store it in cache (valid for 15 min)
        token = get_random_string(32)
        cache.set(f"pwdreset:{token}", user.id, timeout=900)
        reset_link = f"http://localhost:3000/reset-password/{token}"
        print(f"[MOCK EMAIL] Password reset link for {email}: {reset_link}")
        return Response({"message": "Password reset link sent (mocked)."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        user_id = cache.get(f"pwdreset:{token}")
        if not user_id:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        new_password = request.data.get("new_password", "")
        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()
        cache.delete(f"pwdreset:{token}")
        return Response({"message": "Password has been reset successfully."})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (
            request.data.get("email", request.data.get("username", "")).strip().lower()
        )
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists. Please use another email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check password length
        password = request.data.get("password", "")
        if not password:
            return Response(
                {"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserRegistrationSerializer(
            data={"email": email, "password": password}
        )
        if serializer.is_valid():
            user = serializer.save()

            # Create user preferences
            # UserPreferences.objects.create(user=user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "User registered successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        # Handle validation errors
        errors = []
        for field, error_list in serializer.errors.items():
            for error in error_list:
                errors.append(f"{field}: {error}")

        return Response(
            {"error": "; ".join(errors) if errors else "Registration failed"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password")

        # Check if fields are provided
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user exists
        try:
            user_exists = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Email does not exist. Please check your email or sign up."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check if account is active
        if not user_exists.is_active:
            return Response(
                {"error": "Your account has been disabled. Please contact support."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Authenticate user
        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "Login successful",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid password. Please check your password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to logout

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                # If no refresh token provided, just return success
                # Frontend will clear localStorage anyway
                return Response(
                    {"message": "Logout successful"}, status=status.HTTP_200_OK
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            # Even if token blacklisting fails, consider logout successful
            # since the frontend will clear the tokens anyway
            print(f"DEBUG: Logout token blacklist failed: {e}")
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestLoginView(APIView):
    """
    Temporary test login view that bypasses authentication
    FOR TESTING PURPOSES ONLY - REMOVE IN PRODUCTION
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Return mock successful login for any credentials during testing
        return Response(
            {
                "user": {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@moviesvault.com",
                    "first_name": "Test",
                    "last_name": "User",
                },
                "access": "mock_access_token",
                "refresh": "mock_refresh_token",
                "message": "Test login successful",
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"error": "Invalid old password"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.password = make_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully"})


class UserRoleUpdateView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        role = request.data.get("role")

        allowed = {choice[0] for choice in User.UserRole.choices}
        if role not in allowed:
            return Response(
                {"error": "Invalid role. Use admin, manager, or viewer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.role = role
        user.save(update_fields=["role", "updated_at"])
        return Response(
            {"message": "Role updated successfully", "user": UserSerializer(user).data}
        )
