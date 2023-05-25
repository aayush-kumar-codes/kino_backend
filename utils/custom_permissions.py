from rest_framework.permissions import BasePermission
from users.models import User
from enum import Enum
from utils.helper import get_view_permissions


class AdminAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Admin:
            return True
        return False


class TeacherAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Teacher:
            if required_permissions in list(permissions):
                return True
        return False


class StudentAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Student:
            if required_permissions in list(permissions):
                return True
        return False


class ParentAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)

        if request.user and request.user.role == User.Parent:
            if required_permissions in list(permissions):
                return True
        return False


class HeadOfCuricullumAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True

        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Head_of_curicullum:
            if required_permissions in list(permissions):
                return True
        return False


class ContentCreatorAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)

        if request.user and request.user.role in [
            User.Content_creator, User.Head_of_curicullum
        ]:
            if required_permissions in list(permissions):
                return True
        return False


class FinanceAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Finance:
            if required_permissions in list(permissions):
                return True
        return False


class SchoolAdminAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.School_Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Content_creator:
            if required_permissions in list(permissions):
                return True
        return False


class PermissonChoices(Enum):
    NULL = 0
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

    FULL = 13
    TEAM_LEAD = 14
