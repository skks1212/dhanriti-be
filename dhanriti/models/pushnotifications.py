from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.timezone import now

from utils.helpers import get_random_string
from utils.models.base import BaseModel

from .enums import GenreType, VisibilityType
from .users import User



class PushNotificationToken(BaseModel):
    token = models.CharField(max_length=255)
    device = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"Token: {self.token}, User: {self.user}"
