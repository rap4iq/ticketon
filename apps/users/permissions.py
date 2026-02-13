from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class  IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ORGANIZER')

    

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsEventOwnerOrReadOnly(IsOwnerOrReadOnly):
    def has_object_permission(self, request, view, obj):
        # Если объект - это Event
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        # Если объект связан с Event (например, TicketCategory)
        elif hasattr(obj, 'event'):
            return obj.event.organizer == request.user
        
        return False