from django.db.models import IntegerChoices


class FlowRateType(IntegerChoices):
    TIMELY = 1
    CONSEQUENT = 2


class FlowType(IntegerChoices):
    ABSOLUTE = 1
    PERCENTAGE = 2
