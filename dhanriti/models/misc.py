import secrets

from django.db import models

from utils.models.base import BaseModel
from dhanriti.models.enums import PresetType
from dhanriti.models.users import User


class Preset(BaseModel):
    type = models.IntegerField(
        choices=PresetType.choices, default=PresetType.LEAF_BACKGROUND
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    content = models.JSONField(default=dict)
    priority = models.IntegerField(default=0)
    hidden = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)

    def __str__(self):
        return (
            (self.name + " - " if self.name else "")
            + f"{str(PresetType(self.type).name)} - {self.priority}"
            + (" (hidden)" if self.hidden else "")
            + (" (premium)" if self.premium else "")
        )


class Motd(BaseModel):
    icon = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=30, blank=False, null=False)
    message = models.TextField(blank=True, null=True)
    expires_on = models.DateTimeField(blank=True, null=True)
    action = models.JSONField(default=dict, blank=True, null=True)
    display_for = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name_plural = "MOTDs"


class Invite(BaseModel):
    code = models.CharField(max_length=255, blank=False, null=False, unique=True)
    uses = models.IntegerField(default=0)
    max_uses = models.IntegerField(default=1)
    expires_on = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.code}"

    def save(self, *args, **kwargs) -> None:
        if self.uses > self.max_uses:
            raise ValueError("Number of uses cannot be greater than max uses.")

        if not self.pk and not self.code:
            self.code = secrets.token_urlsafe(25)

        return super().save(*args, **kwargs)


class InviteUse(BaseModel):
    invite = models.ForeignKey(
        Invite, on_delete=models.PROTECT, null=False, blank=False
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.user} used {self.invite}"


class EmailPreset(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )
    content = models.TextField(blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.name} - {self.description}"


class Email(BaseModel):
    receiver = models.EmailField(blank=False, null=False)
    sender = models.EmailField(blank=False, null=False)
    template = models.ForeignKey(
        EmailPreset, on_delete=models.PROTECT, null=True, blank=False
    )
    content = models.TextField(blank=True, null=True)
    subject = models.TextField(default="Mail from dhanriti", blank=False, null=False)
    sent = models.BooleanField(default=False)
    meta = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.receiver} - {self.template}"


class Asset(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )
    url = models.URLField(blank=False, null=True)
    meta = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.description}"
