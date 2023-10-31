from django.apps import AppConfig


class dhanritiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dhanriti"

    def ready(self):
        from .signals import (  # noqa: F401
            login_ip,
            notifications,
            push_notifications,
            shelfleaf,
            shelfstory,
            stories,
            update_counts,
        )
