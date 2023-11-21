import random
import re
import string
from django.core.exceptions import ValidationError


def get_random_string(length: int) -> str:
    return "".join(random.choices(string.hexdigits, k=length))


def get_unique_id(length: int) -> str:
    return "".join(
        random.choices(
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-",
            k=length,
        )
    )


def get_client_ip(request):
    if x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
        return x_forwarded_for.split(",")[0].strip()
    else:
        return request.META.get("REMOTE_ADDR")


def is_valid_crontab_expression(expr):
    # Split the expression into its components
    fields = expr.split()

    # There should be exactly 5 fields for a valid crontab expression
    if len(fields) != 5:
        raise ValidationError("Invalid crontab expression")

    # Define the valid ranges for each field
    valid_ranges = {
        0: (0, 59),  # Minute
        1: (0, 23),  # Hour
        2: (1, 31),  # Day of month
        3: (1, 12),  # Month
        4: (0, 7),   # Day of week (0 and 7 are both Sunday)
    }

    # Define a regex pattern for *, numbers, ranges, and lists
    pattern = r"^(\*|(\d+(-\d+)?)(,\d+(-\d+)?)*)(/\d+)?$"

    for i, field in enumerate(fields):
        # Check if the field matches the pattern
        if not re.match(pattern, field):
            raise ValidationError("Invalid crontab expression")

        # If the field is not an asterisk, validate the numbers/ranges
        if field != "*":
            # Split the field by commas to handle lists
            for part in field.split(","):
                # Check for step values (e.g., */5 or 1-10/2)
                if "/" in part:
                    part, step = part.split("/")
                    if not step.isdigit() or int(step) <= 0:
                        raise ValidationError("Invalid crontab expression")

                # Check for ranges (e.g., 1-5)
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    if (
                        start > end
                        or start < valid_ranges[i][0]
                        or end > valid_ranges[i][1]
                    ):
                        raise ValidationError("Invalid crontab expression")
                elif part.isdigit():
                    # Single value
                    value = int(part)
                    if value < valid_ranges[i][0] or value > valid_ranges[i][1]:
                        raise ValidationError("Invalid crontab expression")

    return True