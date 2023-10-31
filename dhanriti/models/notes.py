from django.db import models

from utils.models.base import BaseModel
from dhanriti.models.stories import Part, Story
from dhanriti.models.users import User


class Note(BaseModel):
    title = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    story = models.ForeignKey(
        Story, on_delete=models.PROTECT, blank=True, null=True, to_field="external_id"
    )
    part = models.ForeignKey(
        Part, on_delete=models.PROTECT, blank=True, null=True, to_field="external_id"
    )
    description = models.TextField(blank=True, null=True)
    line = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        verbose_name_plural = "Notes"
