from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

from utils.models.base import BaseModel


class UserManager(BaseUserManager):
    pass


class User(AbstractUser):
    first_name = None
    last_name = None

    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)
    vishnu_id = models.CharField(blank=True, max_length=255, db_index=True)

    full_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(_("email address"), unique=True, db_index=True)

    last_login_platform = models.CharField(max_length=100, blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_online = models.DateTimeField(default=timezone.now)

    modified_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        # Disabled because VISHNU-DEFAULT causes problems
        # if self.username != self.username.lower():
        #    raise ValueError("Username cannot have uppercase letters.")
        return super().save(*args, **kwargs)


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
