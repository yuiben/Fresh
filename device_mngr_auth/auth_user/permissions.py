from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    message = {
        'status':403, 'message': 'You do not have permission to use this action !'}
    
    def has_permission(self, request, view):
        return request.user.role == 1