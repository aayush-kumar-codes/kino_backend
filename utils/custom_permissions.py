from rest_framework.permissions import BasePermission
from users.models import User
from enum import Enum


class AdminAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Admin:
            return True
        return False


class TeacherAccess(BasePermission):
    def has_permission(self, request, view):
        required_permissions = view.get_required_permissions().value
        permissions = request.user.permission.all().values_list(
            "code_id", flat=True
        )
        if request.user and request.user.role == User.Teacher:
            if required_permissions in list(permissions):
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


class PermissonChoices(Enum):
    LESSON_READ = 1
    LESSON_EDIT = 2
    LESSON_DELETE = 3

    SCHOOL_READ = 4
    SCHOOL_EDIT = 5
    SCHOOL_DELETE = 6

    SETTING_ADD = 7
    SETTING_EDIT = 8
    SETTING_DELETE = 9

    TERM_READ = 10
    TERM_EDIT = 11
    TERM_DELETE = 12
