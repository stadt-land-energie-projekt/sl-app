"""Form definitions for the explorer app."""
from __future__ import annotations

from typing import TYPE_CHECKING

from django.forms import BooleanField, Form, renderers
from django.utils.safestring import mark_safe

if TYPE_CHECKING:
    from django_mapengine.legend import LegendLayer

from .widgets import SwitchWidget


class TemplateForm(Form):  # noqa: D101
    template_name = None

    def __str__(self) -> str:  # noqa: D105
        if self.template_name:
            renderer = renderers.get_default_renderer()
            return mark_safe(renderer.render(self.template_name, {"form": self}))  # noqa: S308
        return super().__str__()


class StaticLayerForm(TemplateForm):  # noqa: D101
    template_name = "forms/layer.html"
    switch = BooleanField(
        label=False,
        widget=SwitchWidget(
            attrs={
                "switch_class": "form-check form-switch",
                "switch_input_class": "form-check-input",
            },
        ),
    )

    def __init__(self, layer: LegendLayer, *args, **kwargs) -> None:  # noqa: ANN002, D107
        super().__init__(*args, **kwargs)
        self.layer = layer
