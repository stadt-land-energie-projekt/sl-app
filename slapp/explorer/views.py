import csv

from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Round
from django.http import HttpResponse
from django.shortcuts import render
from django.templatetags.l10n import localize
from django.views.generic import TemplateView
from django_mapengine import views

from .models import Municipality


class MapGLView(TemplateView, views.MapEngineMixin):
    template_name = "pages/map.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        # Add unique session ID
        context = super().get_context_data(**kwargs)

        return context


def municipalities_details(ids):
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
            )
        )
        .annotate(storage_net=Round(Sum("storage__capacity_net", default=0) / 1000, precision=1))
        .annotate(kwk_el_net=Round(Sum("combustion__capacity_net", default=0) / 1000, precision=1))
        .annotate(kwk_th_net=Round(Sum("combustion__th_capacity", default=0) / 1000, precision=1))
    )
    return municipalities


def details_list(request):
    ids = request.GET.getlist("id")
    if ids:
        if len(ids) > 3:
            ids = ids[:-1]
            messages.add_message(request, messages.WARNING, "Es können maximal 3 Gemeinden ausgewählt werden.")
        municipalities = municipalities_details(ids)
    else:
        municipalities = None

    return render(request, "pages/details.html", {"municipalities": municipalities})


def search_municipality(request):
    search_text = request.POST.get("search")
    param_string = request.POST.get("param_string")
    print(param_string)
    if param_string == "/map/details/":
        new_param_string = param_string + "?id="
    else:
        new_param_string = param_string + "&id="

    # look up all municipalities that contain the text
    results = Municipality.objects.filter(name__icontains=search_text)
    return render(
        request, "pages/partials/search-results.html", {"results": results, "new_param_string": new_param_string}
    )


def details_csv(request):
    ids = request.GET.getlist("id")

    if ids:
        municipalities = municipalities_details(ids)
    else:
        municipalities = None

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
