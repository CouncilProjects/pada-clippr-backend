from rest_framework import permissions

class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.get_role_name() == 'MEMBER'

class IsVerifiedSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.get_role_name() == 'SELLER'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.get_role_name() == 'ADMIN'
