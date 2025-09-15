from rest_framework import permissions

class IsInGroup(permissions.BasePermission):
    """
    Allows access only to users in a specific group.
    """
    def __init__(self, group_name):
        self.group_name = group_name

    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.groups.filter(name=self.group_name).exists()
        )

# Helper functions for common groups
class IsEmployee(IsInGroup):
    def __init__(self):
        super().__init__("Employee")

class IsManager(IsInGroup):
    def __init__(self):
        super().__init__("Manager")
