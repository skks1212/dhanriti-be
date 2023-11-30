from dhanriti.models.tanks import Tank
from utils.models.base import BaseModel
from django.db import models

class Payment(BaseModel):
    amount = models.FloatField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    tank = models.ForeignKey(
        Tank, on_delete=models.CASCADE, blank=False, null=False, related_name="payments"
    )
