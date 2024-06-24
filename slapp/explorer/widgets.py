"""Module holds widgets for digiplan."""

from django.forms.widgets import Widget


class SliderWidget(Widget):
    """Widget to render sliders."""

    template_name = "widgets/slider.html"
