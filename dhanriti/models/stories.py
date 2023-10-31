from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.timezone import now

from utils.helpers import get_random_string
from utils.models.base import BaseModel

from .enums import GenreType, VisibilityType
from .users import User


class Story(BaseModel):
    url = models.CharField(
        max_length=16, unique=True, db_index=True, blank=True, null=True
    )
    title = models.CharField(max_length=150, blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)
    cover = models.TextField(blank=True, null=True)
    genre = models.IntegerField(choices=GenreType.choices)
    reads = models.IntegerField(default=0)
    claps = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    visibility = models.IntegerField(
        choices=VisibilityType.choices, default=VisibilityType.PRIVATE
    )
    language = models.CharField(
        max_length=2,
        default="EN",
        help_text="ISO 639-1 language codes",
    )
    parts_order = ArrayField(
        models.CharField(max_length=100), default=list, blank=True, null=True
    )

    explicit = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    published_on = models.DateTimeField(null=True, blank=True)
    last_worked_on = models.DateTimeField(null=True, blank=True)
    allow_comments = models.BooleanField(default=True)
    tags = ArrayField(
        models.CharField(max_length=100), default=list, blank=True, null=True
    )
    preference_points = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"

    def save(self, *args, **kwargs) -> None:
        if not self.published_on and self.visibility == VisibilityType.PUBLIC:
            self.published_on = now()
        self.language = self.language.upper()
        if not self.url:
            unique_id = get_random_string(8)
            while self.__class__.objects.filter(url=unique_id):
                unique_id = get_random_string(8)
            self.url = unique_id

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Stories"


class Part(BaseModel):
    url = models.CharField(
        max_length=16, unique=True, db_index=True, blank=True, null=True
    )
    story = models.ForeignKey(
        Story, on_delete=models.PROTECT, db_index=True, related_name="parts"
    )
    title = models.CharField(max_length=100, blank=False, null=False)
    content = models.TextField(blank=True, null=True)
    unpublished_content = models.TextField(blank=True, null=True)
    visibility = models.IntegerField(
        choices=VisibilityType.choices, default=VisibilityType.PRIVATE
    )
    published_on = models.DateTimeField(null=True, blank=True)
    last_worked_on = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.title} in {self.story}"

    def save(self, *args, **kwargs) -> None:
        if not self.published_on and self.visibility == VisibilityType.PUBLIC:
            self.published_on = now()
        if not self.url:
            unique_id = get_random_string(8)
            while self.__class__.objects.filter(url=unique_id):
                unique_id = get_random_string(8)
            self.url = unique_id

        return super().save(*args, **kwargs)


class StoryRead(BaseModel):
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    reader = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    reader_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.reader or self.reader_ip} read {self.part}"
