from django.apps import AppConfig


class dhanritiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dhanriti"

    def ready(self):
        # from .signals import
        pass
