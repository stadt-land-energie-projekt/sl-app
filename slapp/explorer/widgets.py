"""Module holds widgets for digiplan."""

from django.forms.widgets import Widget


class SwitchWidget(Widget):
    """Widget to render switches."""

    template_name = "widgets/switch.html"
