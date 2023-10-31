from django.db import models

from utils.models.base import BaseModel

from .leaves import Leaf
from .stories import Part
from .users import User


class Clap(BaseModel):
    part = models.ForeignKey(Part, on_delete=models.PROTECT, null=True, blank=True)
    leaf = models.ForeignKey(Leaf, on_delete=models.PROTECT, null=True, blank=True)
    clapper = models.ForeignKey(User, on_delete=models.PROTECT)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self) -> str:
        if self.part:
            return f"{self.clapper} clapped for {self.part}"
        elif self.leaf:
            return f"{self.clapper} clapped for {self.leaf}"

    def save(self, *args, **kwargs) -> None:
        if not self.part and not self.leaf:
            raise ValueError("Either 'part' or 'leaf' field must have a value.")
        return super().save(*args, **kwargs)
