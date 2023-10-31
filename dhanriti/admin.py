from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from djangoql.admin import DjangoQLSearchMixin
from simple_history.admin import SimpleHistoryAdmin

from dhanriti.models.tanks import Canvas, Flow, Funnel, Tank

from .models import (
    Login,
    User,
)


@admin.register(User)
class UserAdmin(DjangoQLSearchMixin, BaseUserAdmin):
    list_display = (
        "id",
        "vishnu_id",
        "username",
        "email",
        "full_name",
        "is_staff",
    )
    list_display_links = list_display
    filter_horizontal = (*BaseUserAdmin.filter_horizontal,)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "username",
                    "password",
                    "external_id",
                    "vishnu_id",
                )
            },
        ),
        (
            "User info",
            {
                "fields": (
                    "full_name",
                    "last_login_platform",
                    "last_login_ip",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "modified_at",
                    "date_joined",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    readonly_fields = ("modified_at", "last_login", "date_joined")


@admin.register(Login)
class LoginAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Canvas)
class CanvasAdmin(admin.ModelAdmin):
    pass


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    pass


@admin.register(Funnel)
class FunnelAdmin(admin.ModelAdmin):
    pass


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    pass


admin.site.site_header = "Dhanriti Admin"
