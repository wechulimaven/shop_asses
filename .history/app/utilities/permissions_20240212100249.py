from rest_framework import permissions

class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsAccountVerified(permissions.BasePermission):
    message = "User account is not verified. Go to account Settings page to verify your account."

    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS) or (
            request.user and request.user.is_account_verified
        ):
            return True
        return False


class IsStaff(permissions.BasePermission):
    message = "Operation only reserved for staff"

    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS) or (
            request.user and request.user.is_staff
        ):
            return True
        return False
