"""Module containing django forms."""
from __future__ import annotations

from typing import TYPE_CHECKING

from django.forms import BooleanField, ChoiceField, FloatField, Form, TextInput, renderers
from django.utils.safestring import mark_safe

from .settings import REGIONS

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


class ParametersSliderForm(Form):  # noqa: D101
    def __init__(self, parameters, **kwargs) -> None:  # noqa: D107, ANN001
        super().__init__(**kwargs)
        self.fields = {item["name"]: item["field"] for item in self.generate_fields(parameters)}

    def get_field_attrs(self, name: str, parameters: dict) -> dict:  # noqa: ARG002
        """Set up field attributes from parameters."""
        attrs = {
            "class": parameters["class"],
            "data-min": parameters["min"],
            "data-max": parameters["max"],
            "data-from": parameters["from"],
            "data-grid": "true" if parameters.get("grid") else "false",
            "data-has-sidepanel": "true" if "sidepanel" in parameters else "false",
            "data-color": parameters.get("color", ""),
        }
        if "to" in parameters:
            attrs["data-to"] = parameters["to"]
        if "step" in parameters:
            attrs["data-step"] = parameters["step"]
        if "from-min" in parameters:
            attrs["data-from-min"] = parameters["from-min"]
        if "from-max" in parameters:
            attrs["data-from-max"] = parameters["from-max"]
        return attrs

    def generate_fields(self, parameters: dict) -> dict:  # noqa: D102
        for name, item in parameters.items():
            field = FloatField(
                widget=TextInput(attrs=self.get_field_attrs(name, parameters=item)),
                required=item.get("required", True),
            )
            yield {"name": name, "field": field}


class RegionForm(Form):
    """Form to select a region."""

    region = ChoiceField(choices=({"single": "Regionen zusammengefasst"} | REGIONS).items())
