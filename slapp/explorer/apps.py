from django.apps import AppConfig


class ExplorerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "slapp.explorer"
    verbose_name = "Explorer"

    def ready(self):
        try:
            import slapp.explorer.signals  # noqa: F401
        except ImportError:
            pass
