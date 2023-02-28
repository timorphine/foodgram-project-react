from rest_framework import permissions


class UserIsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомный пермишен, дающий доступ ко всем действиям только автору."""

    def has_object_permission(self, request, view, obj):

        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )


class IsAdmin(permissions.BasePermission):
    """Кастомный пермишен, который расширит возможности встроенных пермишенов
    и разрешит полный доступ к объекту только админу(суперюзеру)"""

    def has_permission(self, request, view):

        user = request.user

        return (
            user.is_authenticated and user.is_admin
            or user.is_superuser
        )

    def has_object_permission(self, request, view, obj):

        user = request.user

        return (
            user.is_authenticated and user.is_admin
            or user.is_superuser
        )
