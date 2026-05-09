from rest_framework import permissions
import os

B2B_SERVICE_KEY = os.environ.get("B2B_SERVICE_KEY")

class IsService(permissions.BasePermission):
    def has_permission(self, request, view):
        service_key = request.headers.get("X-Service-Key")
        if service_key and service_key == B2B_SERVICE_KEY:
            request.is_from_service = True
            return True
        
        request.is_from_service = False
        return False