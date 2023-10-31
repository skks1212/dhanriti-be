from django.db import models

from utils.models.base import BaseModel

from .enums import RarityType
from .users import User


class Badge(BaseModel):
    icon = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    rarity = models.IntegerField(choices=RarityType.choices, default=RarityType.COMMON)

    def __str__(self) -> str:
        return f"{self.name}"


class AssignedBadge(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    badge = models.ForeignKey(Badge, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.badge} assigned to {self.user}"

    class Meta:
        verbose_name_plural = "Assigned Badges"
