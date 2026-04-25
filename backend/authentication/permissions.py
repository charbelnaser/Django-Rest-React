from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.UserRole.ADMIN
        )


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {User.UserRole.ADMIN, User.UserRole.MANAGER}
        )


class IsAdminOrManagerReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role in {User.UserRole.ADMIN, User.UserRole.MANAGER}


class IsAdminReadOnlyForOthers(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role == User.UserRole.ADMIN


class IsAdminManagerWriteAdminDelete(BasePermission):
    """
    Read: admin/manager/viewer
    Create/Update: admin/manager
    Delete: admin only
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == "DELETE":
            return request.user.role == User.UserRole.ADMIN

        return request.user.role in {User.UserRole.ADMIN, User.UserRole.MANAGER}
