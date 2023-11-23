from dhanriti.models.enums import FlowRateType, FlowType
from dhanriti.models.users import User
from utils.helpers import is_valid_crontab_expression
from utils.models.base import BaseModel
from django.db import models
from django.db.models.signals import post_save

class BulkCreateSignalManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        a = super(models.Manager,self).bulk_create(objs,**kwargs)
        for i in objs:
            post_save.send(i.__class__, instance=i, created=True, raw=True)
        return a


class Canvas(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, null=False, related_name="canvases"
    )
    filled = models.FloatField(blank=False, null=False, default=0)
    inflow = models.FloatField(blank=False, null=True)
    inflow_rate = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        validators=[is_valid_crontab_expression],
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.inflow} Rs."


class Tank(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    capacity = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    filled = models.FloatField(blank=False, null=False, default=0)
    canvas = models.ForeignKey(
        Canvas, on_delete=models.CASCADE, blank=False, null=False, related_name="tanks"
    )

    def __str__(self) -> str:
        return f"{self.name} - {self.capacity} Rs."


class Funnel(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    flow_rate = models.CharField(
        max_length=255, blank=False, null=True, validators=[is_valid_crontab_expression]
    )
    flow_rate_type = models.IntegerField(choices=FlowRateType.choices)
    flow = models.FloatField(blank=False, null=True)
    flow_type = models.IntegerField(choices=FlowType.choices)
    in_tank = models.ForeignKey(
        Tank, on_delete=models.CASCADE, blank=False, null=True, related_name="funnels"
    )
    out_tank = models.ForeignKey(
        Tank,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="parent_funnel",
    )
    canvas= models.ForeignKey(
        Canvas,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name="funnels",
    )


class Flow(BaseModel):
    objects = BulkCreateSignalManager()
    funnel = models.ForeignKey(
        Funnel, on_delete=models.CASCADE, blank=False, null=True, related_name="flows"
    )
    canvas = models.ForeignKey(
        Canvas, on_delete=models.CASCADE, blank=False, null=True, related_name="flows"
    )
    flowed = models.FloatField(blank=False, null=True)
    manual = models.BooleanField(default=False)
    meta = models.JSONField(blank=True, null=True)