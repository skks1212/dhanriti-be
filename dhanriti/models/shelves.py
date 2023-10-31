from django.contrib.postgres.fields import ArrayField
from django.db import models

from utils.models.base import BaseModel

from .enums import VisibilityType
from .leaves import Leaf
from .stories import Story
from .users import User


class Shelf(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, null=True)
    visibility = models.IntegerField(
        choices=VisibilityType.choices, default=VisibilityType.PRIVATE
    )
    last_interaction = models.DateTimeField(null=True, blank=True)
    cover = models.TextField(blank=True, null=True)
    story_order = ArrayField(
        models.CharField(max_length=100), default=list, blank=True, null=True
    )
    leaf_order = ArrayField(
        models.CharField(max_length=100), default=list, blank=True, null=True
    )
    stories = models.ManyToManyField(Story, through="ShelfStory")
    leaves = models.ManyToManyField(Leaf, through="ShelfLeaf")

    def __str__(self):
        return f"{self.user}'s {self.name}"

    class Meta:
        verbose_name_plural = "Shelves"


class ShelfStory(BaseModel):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=False, blank=False)
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.story} in {self.shelf}"

    class Meta:
        verbose_name_plural = "Shelf Stories"


class ShelfLeaf(BaseModel):
    leaf = models.ForeignKey(Leaf, on_delete=models.CASCADE, null=False, blank=False)
    shelf = models.ForeignKey(Shelf, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.leaf} in {self.shelf}"

    class Meta:
        verbose_name_plural = "Shelf Leaves"
