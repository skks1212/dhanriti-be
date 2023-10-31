from django.db import models

from utils.models.base import BaseModel
from dhanriti.models.stories import Part, Story
from dhanriti.models.users import User


class Search(BaseModel):
    query = models.CharField(max_length=50)
    search_ip = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.query} by {self.user}"

    class Meta:
        verbose_name_plural = "Searches"
