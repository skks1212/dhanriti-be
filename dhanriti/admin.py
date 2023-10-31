from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from djangoql.admin import DjangoQLSearchMixin
from simple_history.admin import SimpleHistoryAdmin

from dhanriti.models.misc import Invite, InviteUse

from .models import (
    AssignedBadge,
    Award,
    Awarded,
    Badge,
    Clap,
    Comment,
    CommentLike,
    Email,
    EmailPreset,
    Follow,
    Leaf,
    LeafRead,
    Login,
    Motd,
    Note,
    Notification,
    Part,
    Preset,
    PushNotificationToken,
    Report,
    Search,
    Shelf,
    ShelfLeaf,
    ShelfStory,
    Story,
    StoryRead,
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
                    "pronouns",
                    "profile_picture",
                    "backdrop",
                    "about",
                    "notification_settings",
                    "country",
                    "badges_order",
                    "premium",
                    "preference_points",
                    "verified",
                    "closed_beta",
                    "story_language",
                    "last_login_platform",
                    "last_login_ip",
                    "account_setup",
                    "is_bot",
                    "ip_country",
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


@admin.register(Follow)
class FollowAdmin(DjangoQLSearchMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    pass


@admin.register(Notification)
class NotificationAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Story)
class StoryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Part)
class PartAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Leaf)
class LeafAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(LeafRead)
class LeafReadAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(StoryRead)
class StoryReadAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    form = CommentClapAdminForm


@admin.register(Clap)
class ClapAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    form = CommentClapAdminForm


@admin.register(Shelf)
class ShelfAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(CommentLike)
class CommentLikeAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(ShelfStory)
class ShelfStoryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(ShelfLeaf)
class ShelfLeafAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Note)
class NoteAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Search)
class SearchAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(PushNotificationToken)
class PushNotificationTokenAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Badge)
class BadgeAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(AssignedBadge)
class AssignedBadgeAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Award)
class AwardAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Awarded)
class AwardedAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Login)
class LoginAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Preset)
class PresetAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Motd)
class MotdAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Invite)
class InviteAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(InviteUse)
class InviteUseAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(EmailPreset)
class EmailPresetAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


@admin.register(Email)
class EmailAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    pass


admin.site.site_header = "dhanriti Admin"
