from rest_framework import permissions

from core.settings.base import CLOSED_BETA


class IsSelfOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsUserOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAuthorOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthor(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsStoryAuthorOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.story.author == request.user


class HasClosedBetaAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if (
            not CLOSED_BETA
            or request.user.is_staff
            or "setup" in request.path
            or "invites" in request.path
            or "presets" in request.path
            or "users" in request.path
        ):
            return True
        return request.user.is_authenticated and request.user.closed_beta
