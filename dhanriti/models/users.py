import re
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from rest_framework.authtoken.models import Token

from utils.models.base import BaseModel


@deconstructible
class LanguageCodesValidator(validators.RegexValidator):
    regex = r"^(?:[A-Z]{2},){0,4}[A-Z]{2}$"
    flags = re.ASCII
    message = _(
        "Provide comma separated ISO 639-1 language codes. "
        "Maximum of 5 languages allowed."
    )


@deconstructible
class BadgeOrderValidator(validators.RegexValidator):
    regex = r"^(?:\d{1,6},){0,2}\d{1,6}$"
    flags = re.ASCII
    message = _("Provide comma separated badge IDs. Maximum 3 badges are allowed.")


@deconstructible
class CommaUUIDOrderValidator(validators.RegexValidator):
    flags = re.ASCII
    message = _("Provide comma separated UUIDs.")
    # regex for comma separated UUIDs
    regex = r"^(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12},){0,}[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


class UserManager(BaseUserManager):
    pass


def default_notification_settings():
    return {
        "allow_email_notifs": True,
        "allow_push_notifs": True,
    }


class User(AbstractUser):
    first_name = None
    last_name = None

    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)
    vishnu_id = models.CharField(blank=True, max_length=255, db_index=True)
    account_setup = models.BooleanField(default=False)
    closed_beta = models.BooleanField(default=False)

    full_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    profile_picture = models.TextField(blank=True, null=True)
    backdrop = models.TextField(blank=True, null=True)
    about = models.TextField(blank=True)
    pronouns = models.CharField(max_length=10, blank=True, null=True)
    country = CountryField(blank=True)
    notification_settings = models.JSONField(default=default_notification_settings)
    badges_order = ArrayField(
        models.CharField(max_length=100), default=list, blank=True
    )
    preference_points = models.IntegerField(default=0)
    notes_order = models.TextField(
        blank=True, null=True, validators=(CommaUUIDOrderValidator(),)
    )
    premium = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    story_language = models.CharField(
        max_length=50,
        default="EN",
        help_text="Comma separated ISO 639-1 language codes",
        validators=(LanguageCodesValidator(),),
    )

    last_login_platform = models.CharField(max_length=100, blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_online = models.DateTimeField(default=timezone.now)
    ip_country = CountryField(blank=True, null=True)

    modified_at = models.DateTimeField(auto_now=True)

    is_bot = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Disabled because VISHNU-DEFAULT causes problems
        # if self.username != self.username.lower():
        #    raise ValueError("Username cannot have uppercase letters.")
        return super().save(*args, **kwargs)


class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name="following", on_delete=models.PROTECT
    )
    followed = models.ForeignKey(
        User, related_name="followers", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.follower} -> {self.followed}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"], name="unique_follow"
            )
        ]


class Login(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    service_token = models.CharField(max_length=258, null=True, blank=True)
    successful = models.BooleanField(default=False)
    login_at = models.DateTimeField(null=True, blank=True)
    platform = models.CharField(max_length=100, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    token = models.ForeignKey(
        Token, on_delete=models.CASCADE, null=True, blank=True, to_field="key"
    )

    def save(self, *args, **kwargs):
        if self.pk:
            login = Login.objects.get(pk=self.pk)
            if self.successful and not login.successful and self.user:
                self.successful = True
                self.login_at = timezone.now()
                token, _ = Token.objects.get_or_create(user=self.user)
                self.token = token

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user} logged in from {self.platform}"
