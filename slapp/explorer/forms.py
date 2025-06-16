"""Module containing django forms."""

from django.forms import ChoiceField, FloatField, Form, TextInput

from .settings import REGIONS


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
