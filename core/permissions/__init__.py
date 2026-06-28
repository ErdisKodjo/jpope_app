from rest_framework.permissions import BasePermission

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "STUDENT"

class IsCounselor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "COUNSELOR"

class IsSchoolRep(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "SCHOOL_REP"

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.is_authenticated and request.user.role == "ADMIN"
