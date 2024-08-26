"""Explorer views."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Round
from django.http import HttpResponse, JsonResponse

if TYPE_CHECKING:
    from django.http.request import HttpRequest

import json

from django.shortcuts import render
from django.templatetags.l10n import localize
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django_mapengine import views

from .forms import ParametersSliderForm
from .models import Municipality, Region

MAX_MUNICIPALITY_COUNT = 3


def start_page(request: HttpRequest) -> HttpResponse:
    """Render the start / home page."""
    next_url = reverse("explorer:map")
    prev_url = None
    active_tab = "step_1_start"
    sidepanel = False

    ids = request.session.get("municipality_ids", [])
    muns = Municipality.objects.filter(id__in=ids) if ids else None

    context = {
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
        "municipalities": muns
    }
    return render(request, "pages/home.html", context)


class MapGLView(TemplateView, views.MapEngineMixin):
    """Single view for the map."""

    template_name = "pages/map.html"
    regions = Region.objects.all()
    next_url = reverse_lazy("explorer:details")
    prev_url = reverse_lazy("explorer:home")
    active_tab = "step_2_today"
    sidepanel = True
    extra_context = {
        "regions": regions,
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
    }

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Adapt mapengine context."""
        context = super().get_context_data(**kwargs)

        ids = self.request.session.get("municipality_ids", [])
        if ids:
            muns = Municipality.objects.filter(id__in=ids)
            context["municipalities"] = muns

        context["mapengine_store_cold_init"]["fly_to_clicked_feature"] = False
        return context


def municipalities_details(ids: list[int]) -> list[Municipality]:
    """Return municipalities."""
    municipalities = (
        Municipality.objects.filter(id__in=ids)
        .annotate(area_rounded=Round("area", precision=1))
        .annotate(biomass_net=Round(Sum("biomass__capacity_net", default=0) / 1000, precision=1))
        .annotate(pvground_net=Round(Sum("pvground__capacity_net", default=0) / 1000, precision=1))
        .annotate(pvroof_net=Round(Sum("pvroof__capacity_net", default=0) / 1000, precision=1))
        .annotate(wind_net=Round(Sum("windturbine__capacity_net", default=0) / 1000, precision=1))
        .annotate(hydro_net=Round(Sum("hydro__capacity_net", default=0) / 1000, precision=1))
        .annotate(
            total_net=Round(
                (
                    Sum("windturbine__capacity_net", default=0)
                    + Sum("hydro__capacity_net", default=0)
                    + Sum("pvroof__capacity_net", default=0)
                    + Sum("pvground__capacity_net", default=0)
                    + Sum("biomass__capacity_net", default=0)
                )
                / 1000,
                precision=1,
            ),
        )
        .annotate(storage_net=Round(Sum("storage__capacity_net", default=0) / 1000, precision=1))
        .annotate(kwk_el_net=Round(Sum("combustion__capacity_net", default=0) / 1000, precision=1))
        .annotate(kwk_th_net=Round(Sum("combustion__th_capacity", default=0) / 1000, precision=1))
    )
    return municipalities


def details_list(request: HttpRequest) -> HttpResponse:
    """Render details page for given municipality IDs."""
    ids = request.session.get("municipality_ids", [])
    if ids:
        if len(ids) > MAX_MUNICIPALITY_COUNT:
            ids = ids[:MAX_MUNICIPALITY_COUNT]
            messages.add_message(request, messages.WARNING, "Es können maximal 3 Gemeinden ausgewählt werden.")
        municipalities = municipalities_details(ids)
    else:
        municipalities = None

    next_url = reverse("explorer:esm_mode")
    prev_url = reverse("explorer:map")
    active_tab = "step_3_details"
    sidepanel = True

    context = {
        "municipalities": municipalities,
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
    }

    return render(request, "pages/details.html", context)

def load_municipalities(request: HttpRequest) -> HttpResponse:
    """Return list of municipalities for chosen region."""
    region_id = request.GET.get("region_select")

    # Post request when municipalities get reset
    if request.method == "POST":
        request.session.pop("municipality_ids", None)
        return JsonResponse({"status": "success"})

    if region_id:
        region = Region.objects.get(id=region_id)
        muns = Municipality.objects.filter(region=region)
        content = "".join([f'<option value="{mun.id}">{mun.name}</option>' for mun in muns])
    else:
        messages.add_message(request, messages.WARNING, "Es wurde noch keine Gemeinde ausgewählt.")
        content = "<option value=>Wählen Sie eine Gemeinde</option>"
    return HttpResponse(content, content_type="text/html")


def muns_to_banner(request: HttpRequest) -> HttpResponse:
    """Return chosen municipalities for banner."""
    mun_ids = request.POST.getlist("municipality_select")

    # ids for use in other views / templates
    request.session["municipality_ids"] = mun_ids

    muns = Municipality.objects.filter(id__in=mun_ids)
    return render(
        request,
        "pages/partials/banner.html",
        {"municipalities": muns},
    )


def search_municipality(request: HttpRequest) -> HttpResponse:
    """Return list of municipalities for given search text."""
    search_text = request.POST.get("search")
    param_string = request.POST.get("param_string")

    first_item = param_string in ["/explorer/details/", "/explorer/parameters_variation/"]

    new_param_string = param_string + "?id=" if first_item else param_string + "&id="

    # look up all municipalities that contain the text
    results = Municipality.objects.filter(name__icontains=search_text)
    return render(
        request,
        "pages/partials/search-results.html",
        {"results": results, "new_param_string": new_param_string},
    )


def details_csv(request: HttpRequest) -> HttpResponse:
    """Return details as CSV for given municipalities."""
    ids = request.session.get("municipality_ids", [])
    municipalities = municipalities_details(ids) if ids else None

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="sl-app_gemeinden-details.csv"'},
    )
    data = list(municipalities.values())
    writer = csv.writer(response)
    writer.writerow(["Gemeinde", *[item["name"] for item in data]])
    writer.writerow(["Fläche", *[localize(item["area_rounded"]) for item in data], "km²"])
    writer.writerow(["erneuerbare Stromerzeugung"])
    writer.writerow(["Freiflächen-PV", *[localize(item["pvground_net"]) for item in data], "kW"])
    writer.writerow(["Windkraft", *[localize(item["wind_net"]) for item in data], "kW"])
    writer.writerow(["Biomasse", *[localize(item["biomass_net"]) for item in data], "kW"])
    writer.writerow(["Wasserkraft", *[localize(item["hydro_net"]) for item in data], "kW"])
    writer.writerow(["Stromspeicher"])
    writer.writerow(["Speicherkapazität", *[localize(item["storage_net"]) for item in data], "kWh"])
    writer.writerow(["Wärmegewinnung (KWK)"])
    writer.writerow(["thermische Leistung", *[localize(item["kwk_th_net"]) for item in data], "kW"])
    writer.writerow(["elektrische Leistung", *[localize(item["kwk_el_net"]) for item in data], "kW"])
    return response


def choose_esm_mode(request: HttpRequest) -> HttpResponse:
    """Render page for choosing esm mode (robust or variation)."""
    next_url = None
    prev_url = reverse("explorer:details")
    active_tab = "step_4_mode"
    sidepanel = True
    render_template = "pages/esm_mode.html"
    radio_button_value = int(request.GET.get("esm_choice_radio", 0))
    variation_chosen = 1
    robustness_chosen = 2

    if radio_button_value == variation_chosen:
        next_url = reverse("explorer:parameters_variation")
        render_template = "pages/partials/next_wizard.html"
    if radio_button_value == robustness_chosen:
        next_url = reverse("explorer:parameters_robustness")
        render_template = "pages/partials/next_wizard.html"

    ids = request.session.get("municipality_ids", [])
    muns = Municipality.objects.filter(id__in=ids) if ids else None

    context = {
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
        "municipalities": muns
    }
    return render(request, render_template, context)


def optimization_parameters(request: HttpRequest) -> HttpResponse:
    """Render parameters page for given municipality IDs."""
    ids = request.session.get("municipality_ids", [])
    mun_forms = {}
    municipalities = None
    sliders_config = {}

    if ids:
        if len(ids) > MAX_MUNICIPALITY_COUNT:
            ids = ids[:MAX_MUNICIPALITY_COUNT]
            messages.add_message(request, messages.WARNING, "Es können maximal 3 Gemeinden ausgewählt werden.")
        municipalities = Municipality.objects.filter(id__in=ids)
        with open("slapp/static/config/parameters_slider.json") as f:  # noqa: PTH123
            sliders_config = json.load(f)
        for mun in municipalities:
            parameters = sliders_config[str(mun.id)]
            form_instance = ParametersSliderForm(parameters=parameters)
            mun_forms[mun.name] = {
                "id": mun.id,
                "form": form_instance,
            }

    next_url = reverse("explorer:results_variation")
    prev_url = reverse("explorer:esm_mode")
    active_tab = "step_5_parameters"
    sidepanel = True

    context = {
        "municipalities": municipalities,
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
        "sliders_config": sliders_config,
        "mun_forms": mun_forms,
    }

    return render(
        request,
        "pages/parameters_variation.html",
        context,
    )


def optimization_results(request: HttpRequest) -> HttpResponse:
    """Return optimiziation results per municipality."""
    ids = request.session.get("municipality_ids", [])

    if ids:
        if len(ids) > MAX_MUNICIPALITY_COUNT:
            ids = ids[:MAX_MUNICIPALITY_COUNT]
            messages.add_message(request, messages.WARNING, "Es können maximal 3 Gemeinden ausgewählt werden.")
        municipalities = municipalities_details(ids)
        messages.add_message(
            request,
            messages.WARNING,
            "Die Werte werden aktuell noch nicht wirklich berechnet und dienen nur Anschauungszwecken.",
        )

        for municipality in municipalities:
            municipality.biomass_net_optimized = round(municipality.biomass_net * 1.1, 1)
            municipality.pvground_net_optimized = round(municipality.pvground_net * 1.1, 1)
            municipality.pvroof_net_optimized = round(municipality.pvroof_net * 1.1, 1)
            municipality.wind_net_optimized = round(municipality.wind_net * 1.1, 1)
            municipality.hydro_net_optimized = round(municipality.hydro_net * 1.1, 1)
            municipality.total_net_optimized = round(
                municipality.hydro_net_optimized
                + municipality.wind_net_optimized
                + municipality.biomass_net_optimized
                + municipality.pvground_net_optimized
                + municipality.pvroof_net_optimized,
                1,
            )
            municipality.storage_net_optimized = round(municipality.storage_net * 1.1, 1)
            municipality.kwk_el_net_optimized = round(municipality.kwk_el_net * 1.1, 1)
            municipality.kwk_th_net_optimized = round(municipality.kwk_th_net * 1.1, 1)
    else:
        municipalities = None
        messages.add_message(request, messages.WARNING, "Keine Gemeinde(n) ausgewählt.")

    next_url = reverse("explorer:added_value")
    prev_url = reverse("explorer:parameters_variation")
    active_tab = "step_6_results"
    sidepanel = True
    request.session["prev_before_added_value"] = "variation"

    context = {
        "municipalities": municipalities,
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
    }

    return render(request, "pages/results_variation.html", context)


def robustness_parameters(request: HttpRequest) -> HttpResponse:
    """Render page for robustness parameters."""
    next_url = reverse("explorer:results_robustness")
    prev_url = reverse("explorer:esm_mode")
    active_tab = "step_5_parameters"
    sidepanel = True

    ids = request.session.get("municipality_ids", [])
    muns = Municipality.objects.filter(id__in=ids) if ids else None

    context = {
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
        "municipalities": muns
    }
    return render(request, "pages/parameters_robustness.html", context)


def robustness(request: HttpRequest) -> HttpResponse:
    """Render robustness page."""
    ids = request.session.get("municipality_ids", [])

    if ids:
        if len(ids) > MAX_MUNICIPALITY_COUNT:
            ids = ids[:MAX_MUNICIPALITY_COUNT]
            messages.add_message(request, messages.WARNING, "Es können maximal 3 Gemeinden ausgewählt werden.")
        municipalities = municipalities_details(ids)
        messages.add_message(
            request,
            messages.WARNING,
            "Die Werte werden aktuell noch nicht wirklich berechnet und dienen nur Anschauungszwecken.",
        )

        for municipality in municipalities:
            municipality.biomass_net_optimized = round(municipality.biomass_net * 1.1, 1)
            municipality.pvground_net_optimized = round(municipality.pvground_net * 1.1, 1)
            municipality.pvroof_net_optimized = round(municipality.pvroof_net * 1.1, 1)
            municipality.wind_net_optimized = round(municipality.wind_net * 1.1, 1)
            municipality.hydro_net_optimized = round(municipality.hydro_net * 1.1, 1)
            municipality.total_net_optimized = round(
                municipality.hydro_net_optimized
                + municipality.wind_net_optimized
                + municipality.biomass_net_optimized
                + municipality.pvground_net_optimized
                + municipality.pvroof_net_optimized,
                1,
            )
            municipality.storage_net_optimized = round(municipality.storage_net * 1.1, 1)
            municipality.kwk_el_net_optimized = round(municipality.kwk_el_net * 1.1, 1)
            municipality.kwk_th_net_optimized = round(municipality.kwk_th_net * 1.1, 1)

        for municipality in municipalities:
            municipality.biomass_net_robust = round(municipality.biomass_net * 1.0, 1)
            municipality.pvground_net_robust = round(municipality.pvground_net * 1.2, 1)
            municipality.pvroof_net_robust = round(municipality.pvroof_net * 1.3, 1)
            municipality.wind_net_robust = round(municipality.wind_net * 1.0, 1)
            municipality.hydro_net_robust = round(municipality.hydro_net * 1.0, 1)
            municipality.total_net_robust = round(
                municipality.hydro_net_robust
                + municipality.wind_net_robust
                + municipality.biomass_net_robust
                + municipality.pvground_net_robust
                + municipality.pvroof_net_robust,
                1,
            )
            municipality.storage_net_robust = round(municipality.storage_net * 1.2, 1)
            municipality.kwk_el_net_robust = round(municipality.kwk_el_net * 1.0, 1)
            municipality.kwk_th_net_robust = round(municipality.kwk_th_net * 1.2, 1)

    else:
        municipalities = None
        messages.add_message(request, messages.WARNING, "Keine Gemeinde(n) ausgewählt.")

    next_url = reverse("explorer:added_value")
    prev_url = reverse("explorer:parameters_robustness")
    active_tab = "step_6_results"
    sidepanel = True
    request.session["prev_before_added_value"] = "robustness"

    context = {
        "municipalities": municipalities,
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
    }

    return render(request, "pages/results_robustness.html", context)


def added_value(request: HttpRequest) -> HttpResponse:
    """Render page for information about 'Wertschöpfung'."""
    next_url = None
    prev_url = reverse("explorer:results_variation")
    active_tab = "step_7_added_value"
    sidepanel = True

    if request.session.get("prev_before_added_value") == "robustness":
        prev_url = reverse("explorer:results_robustness")

    ids = request.session.get("municipality_ids", [])
    muns = Municipality.objects.filter(id__in=ids) if ids else None

    context = {
        "next_url": next_url,
        "prev_url": prev_url,
        "active_tab": active_tab,
        "has_sidepanel": sidepanel,
        "municipalities": muns
    }
    return render(request, "pages/added_value.html", context)


# sets the order of the view flow
menu_tabs = [
    {1: "explorer:home"},
    {2: "explorer:map"},
    {3: "explorer:details"},
    {4: "explorer:esm_mode"},
    {5: "explorer:parameters_variation"},
    {6: "explorer:results_variation"},
    {7: "explorer:added_value"},
    {8: "--- placeholder ---"},
    {9: "explorer:parameters_robustness"},
    {10: "explorer:results_robustness"},
    {11: "explorer:added_value"},
]


def next_menu_tab(request: HttpRequest) -> HttpResponse:
    """Render the next page after click in current page."""
    current_tab = int(request.POST.get("tab_id"))
    variation_end = 7
    if current_tab < len(menu_tabs) and current_tab != variation_end:
        next_tab = current_tab + 1

        for tab_dict in menu_tabs:
            if next_tab in tab_dict:
                view_name = tab_dict[next_tab]

        request.session["current_tab"] = next_tab
        return redirect(reverse(view_name))

    messages.add_message(request, messages.WARNING, "Es geht nicht weiter.")
    template_name = "added_value"
    return render(request, f"pages/{template_name}.html")


def previous_menu_tab(request: HttpRequest) -> HttpResponse:
    """Render the previous page after click in current page."""
    current_tab = int(request.POST.get("tab_id"))
    robust_start = 9
    if current_tab > 1:
        previous_tab = 4 if current_tab == robust_start else current_tab - 1

        for tab_dict in menu_tabs:
            if previous_tab in tab_dict:
                view_name = tab_dict[previous_tab]

        request.session["current_tab"] = previous_tab
        return redirect(reverse(view_name))

    messages.add_message(request, messages.WARNING, "Es geht nicht zurück.")
    template_name = "home"
    return render(request, f"pages/{template_name}.html")


def esm_choice(request: HttpRequest, tab_id: int) -> HttpResponse:  # noqa: ARG001
    """Get wich ESM mode was chosen and changes the tab_id accordingly."""
    variation_start_id = 4
    robust_start_id = 8
    if tab_id == variation_start_id:
        response = "<input id='tab_name' type='hidden' name='tab_id' value='4' />"
    if tab_id == robust_start_id:
        response = "<input id='tab_name' type='hidden' name='tab_id' value='8' />"

    return HttpResponse(response, content_type="text/html")
