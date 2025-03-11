"""Module to calculate results."""

from __future__ import annotations

from .models import Sensitivity

# TODO(sagemaso): This list has to be filled with all technologies and related capacity variable names
#  which should show up in sensitivity chart:
# https://github.com/stadt-land-energie-projekt/sl-app/issues/173
CAPACITIES = {"BB-wind-onshore": "invest_out_electricity"}


def get_sensitivity_result(sensitivity: str, technology: str) -> dict[float, dict[str, float]]:
    """Return resulting capacities for given sensitivity."""
    sensitivities = Sensitivity.objects.filter(attribute=sensitivity, component=technology)
    results = {
        sensitivity.perturbation_parameter: sensitivity.scenario.result_set.filter(name__in=CAPACITIES)
        for sensitivity in sensitivities
    }
    return {
        sensitivity: {
            technology: queryset.filter(name=technology, var_name=capacity).values("var_value").first()["var_value"]
            for technology, capacity in CAPACITIES.items()
        }
        for sensitivity, queryset in results.items()
    }
