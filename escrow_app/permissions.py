from rest_framework.permissions import BasePermission 

class IsActiveVerifiedAuthenticated(BasePermission):
    """
    A base class from which our project should inherit all permission classes.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active and request.user.is_verified)