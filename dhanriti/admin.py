from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from djangoql.admin import DjangoQLSearchMixin
from simple_history.admin import SimpleHistoryAdmin

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


class CommentClapAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        part = cleaned_data.get("part")
        leaf = cleaned_data.get("leaf")
        if not part and not leaf:
            raise forms.ValidationError(
                "Either 'part' or 'leaf' field must have a value."
            )
        return cleaned_data


admin.site.site_header = "Dhanriti Admin"
