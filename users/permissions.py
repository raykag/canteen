from rest_framework import permissions

class IsOwnerOrAdminOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it,
    or admins and staff to edit any object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is admin or staff
        if hasattr(request.user, 'is_admin') and request.user.is_admin:
            return True
        if hasattr(request.user, 'is_staff_member') and request.user.is_staff_member:
            return True
        
        # Write permissions are only allowed to the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user

class IsAdminOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow admins and staff to access the view.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'is_admin') and request.user.is_admin
        ) or (
            hasattr(request.user, 'is_staff_member') and request.user.is_staff_member
        )

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access the view.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'is_admin') and request.user.is_admin

class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow farmers to access the view.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'is_farmer') and request.user.is_farmer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Others can only read.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user