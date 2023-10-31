import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class SlugValidator(validators.RegexValidator):
    regex = r"^(?=.{3,16}$)(?![-])(?!.*[-]{2})[a-zA-Z0-9-]+(?<![-])$"
    message = _(
        "Slug must be 3 to 16 characters long. "
        "It may only contain alphabets, numbers and hyphen. "
        "It shouldn't start or end with hyphens. "
        "It shouldn't contain consecutive hyphens. "
    )
    flags = re.ASCII
