from django.db import models

from utils.helpers import get_random_string
from utils.models.base import BaseModel

from .enums import VisibilityType
from .users import User


class Leaf(BaseModel):
    url = models.CharField(
        max_length=60, unique=True, db_index=True, blank=True, null=True
    )
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    bg_url = models.TextField(blank=True, null=True)
    img_url = models.TextField()
    text = models.TextField(blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    claps = models.IntegerField(default=0)
    reads = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    visibility = models.IntegerField(
        choices=VisibilityType.choices, default=VisibilityType.PRIVATE
    )
    preference_points = models.IntegerField(default=0)
    meta = models.JSONField(default=dict, blank=True, null=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Leaf by {self.author}"

    def save(self, *args, **kwargs) -> None:
        if not self.url:
            unique_id = get_random_string(8)
            while self.__class__.objects.filter(url=unique_id):
                unique_id = get_random_string(8)
            self.url = unique_id

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Leaves"


class LeafRead(BaseModel):
    leaf = models.ForeignKey(Leaf, on_delete=models.PROTECT)
    reader = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    reader_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.reader or self.reader_ip} read {self.leaf}"
