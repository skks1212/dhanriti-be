from django.db import models

from utils.models.base import BaseModel

from .enums import RarityType
from .stories import Part
from .users import User


class Award(BaseModel):
    icon = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=20, blank=False, null=False)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    rarity = models.IntegerField(choices=RarityType.choices, default=RarityType.COMMON)

    def __str__(self) -> str:
        return f"Name : {self.name}, Cost : {self.cost}"


class Awarded(BaseModel):
    award = models.ForeignKey(Award, on_delete=models.PROTECT)
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.TextField()

    def __str__(self) -> str:
        return f"{self.award} awarded by {self.user}"

    class Meta:
        verbose_name_plural = "Awarded"
