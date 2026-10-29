from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to ensure a user only accesses/mutates their own data.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "path") and hasattr(obj.path, "user"):
            return obj.path.user == request.user
        return False
