from rest_framework.permissions import BasePermission
from users.models import User


class AdminAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Admin:
            return True
        return False


class TeacherAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Teacher:
            return True
        return False


class StudentAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Student:
            return True
        return False


class ParentAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Parent:
            return True
        return False


class HeadOfCuricullumAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Head_of_curicullum:
            return True
        return False


class ContentCreatorAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Content_creator:
            return True
        return False


class FinanceAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Finance:
            return True
        return False