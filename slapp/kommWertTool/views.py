"""Views for the kommWertTool: render form and handle submission."""
from pathlib import Path

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from slapp.kommWertTool.cal_mun_rev import main

BASE_DIR = Path(__file__).resolve().parent.parent

muns = [
    {"id": 0, "name": "Gemeinde in Brandenburg"},
]


def index(request: HttpRequest) -> HttpResponse:
    """Render the added value calculation form with default municipality options."""
    try:
        next_url = None
        prev_url = reverse("explorer:results_variation")
        active_tab = "step_7_added_value"
        # sidepanel = True

        if request.session.get("prev_before_added_value") == "robustness":
            prev_url = reverse("explorer:results_robustness")

        # ids = request.session.get("municipality_ids", [])
        # muns = Municipality.objects.filter(id__in=ids) if ids else None

        context = {
            "next_url": next_url,
            "prev_url": prev_url,
            "active_tab": active_tab,
            "municipalities": muns,
        }
        return render(request, "added_value_calc.html", context)
    except Exception as e:
        return HttpResponse(f"Fehler beim Lesen der added_value_calc.html: {e!s}", status=500)


@require_http_methods(["POST"])
def submit(request: HttpRequest) -> HttpResponse:
    """Handle POST submission of the added value form and render results."""
    form_data = request.POST.dict()
    form_data = {k: "0" if v in ["", "Bitte wählen:"] else v for k, v in form_data.items()}

    results = main(form_data)

    try:
        next_url = None
        prev_url = reverse("kommWertTool:added_value")
        active_tab = "step_7_added_value"
        # sidepanel = True

        # ids = request.session.get("municipality_ids", [])
        # muns = Municipality.objects.filter(id__in=ids) if ids else None
        return render(
            request,
            "added_value_results.html",
            {
                "results": results,
                "next_url": next_url,
                "prev_url": prev_url,
                "active_tab": active_tab,
                "municipalities": muns,
            },
        )
    except Exception as e:
        return HttpResponse(f"Fehler beim Lesen der added_value_calc.html: {e!s}", status=500)
