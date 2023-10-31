from django.db import models

from utils.models.base import BaseModel

from .enums import ReportType
from .users import User


class Report(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    type = models.IntegerField(choices=ReportType.choices)
    reported = models.CharField(max_length=100)
    report = models.TextField()
    judgement = models.BooleanField(null=True)
    judge_comment = models.TextField(null=True, blank=True)
    judged_by = models.IntegerField(null=True, blank=True)
    judge_time = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username if self.user else 'Anonymous'}: {ReportType(self.type).label}"
