"""AppConfig for slapp explorer."""
import contextlib

from django.apps import AppConfig


class ExplorerConfig(AppConfig):
    """AppConfig for slapp explorer app."""

    default_auto_field = "django.db.models.AutoField"
    name = "slapp.explorer"
    verbose_name = "Explorer"

    def ready(self) -> None:
        """Try to import signals for explorer app."""
        with contextlib.suppress(ImportError):
            import slapp.explorer.signals  # noqa: F401
