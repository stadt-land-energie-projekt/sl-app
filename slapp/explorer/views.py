from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Round
from django.shortcuts import render
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


def details_list(request):
    ids = request.GET.getlist("id")
    if ids:
        if len(ids) > 3:
            ids = ids[:-1]
            messages.add_message(request, messages.WARNING, "Es können maximal 3 Gemeinden ausgewählt werden.")
        municipalities = (
            Municipality.objects.filter(id__in=ids)
            .values("id", "name")
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
        ).order_by("id", "name")
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
