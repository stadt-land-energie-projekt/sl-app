"""Module containing django forms."""
from django.forms import FloatField, Form, TextInput


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
        for region, param_set in parameters.items():
            for name, item in param_set.items():
                field_name = f"{region}_{name}"
                field = FloatField(
                    widget=TextInput(attrs=self.get_field_attrs(field_name, item)),
                    required=item.get("required", True),
                )
                yield {"name": field_name, "field": field}
