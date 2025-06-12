"""Explorer views."""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.http import HttpResponse, JsonResponse

from . import models

if TYPE_CHECKING:
    from django.http.request import HttpRequest

import json

from django.shortcuts import redirect, render
from django.templatetags.l10n import localize
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django_mapengine import views

from . import charts, results
from .chart_data import REGION_NAME_MAP as OS_REGIONS
from .forms import ParametersSliderForm
from .models import Municipality, Region
from .regions import get_case_studies_charts_data
from .regions import get_regions_data as get_data
from .regions import municipalities_details
from .settings import NODES, TECHNOLOGIES, TECHNOLOGIES_SELECTED

MAX_MUNICIPALITY_COUNT = 3


def start_page(request: HttpRequest) -> HttpResponse:
    """Render the start page and handle form submissions from home.html."""
    if request.method == "POST":
        if "go_to_esys" in request.POST:
            return redirect("explorer:esys_robust")
        if "go_to_added_value" in request.POST:
            return redirect("added_value:index")
    return render(request, "pages/home.html")


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
        "municipalities": muns,
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

    next_url = reverse("kommWertTool:added_value")
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
        "municipalities": muns,
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

    next_url = reverse("kommWertTool:added_value")
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
        "municipalities": muns,
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
    {7: "kommWertTool:added_value"},
    {8: "--- placeholder ---"},
    {9: "explorer:parameters_robustness"},
    {10: "explorer:results_robustness"},
    {11: "kommWertTool:added_value"},
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


class CaseStudies(TemplateView, views.MapEngineMixin):
    """Display the Case Studies page with a list of region data."""

    template_name = "pages/case_studies.html"

    def get_context_data(self, **kwargs) -> dict:
        """Manage context data."""
        context = super().get_context_data(**kwargs)

        try:
            region_kiel = models.Region.objects.get(name="Kiel")
            region_os = models.Region.objects.get(name="Oderland-Spree")
        except models.Region.DoesNotExist:
            region_kiel = None
            region_os = None

        if region_kiel:
            # TODO (henhuy): Select region Kiel
            # https://github.com/stadt-land-energie-projekt/sl-app/issues/242
            ids_kiel = region_kiel.municipality_set.values_list("id", flat=True)
            context["municipalities_region_kiel"] = municipalities_details(ids_kiel)
        else:
            context["municipalities_region_kiel"] = None

        if region_os:
            # TODO (henhuy): Select region Oberland-Spreewald
            # https://github.com/stadt-land-energie-projekt/sl-app/issues/242
            ids_os = region_os.municipality_set.values_list("id", flat=True)
            context["municipalities_region_os"] = municipalities_details(ids_os)
        else:
            context["municipalities_region_os"] = None

        regions = get_data()

        context["regions"] = regions
        context["next_url"] = reverse("explorer:results")
        return context


def all_charts(request: HttpRequest) -> HttpResponse:
    """Build all charts."""
    if request.method != "GET":
        return HttpResponse(status=405)

    region_name = request.GET.get("region", "")

    charts_data = get_case_studies_charts_data(region_name)

    return JsonResponse(charts_data)


class EsysRobust(TemplateView):
    """Display the Esys page with energy system and robustness."""

    template_name = "pages/esys_robust.html"

    def get_context_data(self, **kwargs) -> dict:
        """Manage context data."""
        context = super().get_context_data(**kwargs)

        context["next_url"] = reverse("explorer:case_studies")
        return context


class Results(TemplateView):
    """Display the Results page with central results, basic results and sensitivities."""

    template_name = "pages/results.html"

    def get_context_data(self, **kwargs) -> dict:
        """Manage context data."""
        context = super().get_context_data(**kwargs)

        cost_sensitivity_technologies = (
            models.Sensitivity.objects.filter(attribute="capacity_cost", region="ALL")
            .distinct()
            .values_list("component", flat=True)
        )
        cost_technologies = {tech: TECHNOLOGIES[tech] for tech in cost_sensitivity_technologies}
        cost_technologies = dict(sorted(cost_technologies.items(), key=lambda tech: tech[1]["name"]))

        demand_sensitivity_scenarios = models.Sensitivity.objects.filter(
            attribute="amount",
            region="ALL",
        ).values_list("scenario", "component", "perturbation_parameter")
        demand_technologies = {}
        for scenario_id, component, perturbation in demand_sensitivity_scenarios:
            demand_technologies.setdefault(scenario_id, []).append((component, perturbation))
        demand_technologies_parsed = results.parse_demand_scenario_title(demand_technologies)

        alternatives = results.get_alternative_result("B", 1)

        context["home_url"] = reverse("explorer:home")
        context["added_value_url"] = reverse("added_value:index")
        context["cost_technologies"] = cost_technologies
        context["demand_technologies"] = demand_technologies_parsed
        context["alternatives"] = alternatives
        context["os_regions"] = OS_REGIONS
        context["technologies"] = TECHNOLOGIES
        context["nodes"] = NODES
        context["demand"] = demand_sensitivity_scenarios
        return context


def flow_chart(request: HttpRequest) -> JsonResponse:
    """Return requested data for flow charts on results page."""
    region = request.GET.get("type", "")
    region = "all" if region == "verbu" else "single"
    _, data = charts.electricity_hydro_flow(region)
    return JsonResponse({"flow_data": data})


def cost_capacity_chart(request: HttpRequest) -> HttpResponse:
    """Return either line_data or bar_data."""
    tech = request.GET.get("type", "")
    sensitivity_data = results.get_sensitivity_result("capacity_cost", "ALL", tech)

    if sensitivity_data:
        base_scenario = results.get_base_scenario(var_value__gt=0)
        sensitivity_data[0.0] = base_scenario

    sensitivity_data = results.calculate_capacity_cost_for_technology(tech, sensitivity_data)

    # If an "x" parameter is provided, return tech comparison chart data.
    selected_x = request.GET.get("x")
    if selected_x is not None:
        try:
            selected_x = float(selected_x)
        except ValueError:
            return JsonResponse({"error": "Invalid x value"}, status=400)
        if selected_x not in sensitivity_data:
            return JsonResponse({"error": "x value not found"}, status=404)

        merged_sensitivity_data = results.merge_sensitivity_results(sensitivity_data)
        tech_comp_data_list = results.build_tech_comp_data(merged_sensitivity_data[selected_x], tech)
        return JsonResponse({"bar_data": tech_comp_data_list})

    # Without "x": Create line chart data for the selected technology.
    cost_cap_data = results.build_cost_cap_data(sensitivity_data, tech)
    return JsonResponse({"line_data": cost_cap_data})


def demand_chart(request: HttpRequest) -> JsonResponse:
    """Return demand data."""
    scenario_id = int(request.GET["scenario_id"])
    demand_data = results.get_demand_data(scenario_id)
    return JsonResponse(demand_data)


def demand_capacity_chart(request: HttpRequest) -> JsonResponse:
    """Return demand data."""
    scenario_id = int(request.GET["scenario_id"])
    capacity_data = results.get_demand_capacity_data(scenario_id)
    return JsonResponse({"bar_data": capacity_data})


def basic_charts(request: HttpRequest) -> JsonResponse:
    """Return data for basic charts on results page."""
    region = request.GET.get("type", "")
    if region == "verbu":
        region = "all"
    elif region == "einzeln":
        region = "single"
    basic_charts_data = charts.get_all_base_charts(region)
    return JsonResponse(basic_charts_data)


def ranges(request: HttpRequest) -> JsonResponse:
    """Return requested data for ranges on results page."""
    selected_region = request.GET.get("region")
    region = "B" if selected_region == "kiel" else "BB"
    divergence = float(request.GET.get("divergence", 1)) / 100

    alternatives = results.get_alternative_result(region, divergence)
    alternatives = results.filter_alternatives(alternatives, TECHNOLOGIES_SELECTED)
    for tech, vals in alternatives.items():
        vals["color"] = results.get_technology_color(tech)
        vals["potential"] = results.get_potential(tech) or 0
        vals["potential_unit"] = results.get_potential_unit(tech, vals["potential"])

    alternatives = results.prepare_table_data(alternatives)
    alternatives = dict(sorted(alternatives.items(), key=lambda item: item[1]["max_cost"]))

    return JsonResponse(
        {
            "divergence": divergence,
            "ranges": alternatives,
        },
    )
