from django.db import models
from django.utils import timezone

from utils.models.base import BaseModel

from .enums import NotificationType
from .users import User


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    type = models.IntegerField(choices=NotificationType.choices)
    read = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)

    content = models.JSONField(null=True, blank=True)

    read_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username}: {NotificationType(self.type).label}"

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.read_at and self.read:
            self.read_at = now
        if not self.opened_at and self.opened:
            self.opened_at = now
        super().save(*args, **kwargs)
