from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django_filters import AllValuesMultipleFilter, FilterSet
from django_filters.views import FilterView
from django_mapengine import views

from .models import Municipality


class MapGLView(TemplateView, views.MapEngineMixin):
    template_name = "pages/map.html"
    extra_context = {}

    def get_context_data(self, **kwargs):
        # Add unique session ID
        context = super().get_context_data(**kwargs)

        return context


class MunicipalityFilter(FilterSet):
    name = AllValuesMultipleFilter(field_name="name", lookup_expr="icontains", label=_("Municipality"))

    class Meta:
        model = Municipality
        fields = ["name"]


class MunicipalityListView(FilterView):
    model = Municipality
    filterset_class = MunicipalityFilter
    template_name = "pages/details.html"
    context_object_name = "municipalities"

    queryset = (
        Municipality.objects.all()
        .annotate(biomass_net=Sum("biomass__capacity_net"))
        .annotate(pvground_net=Sum("pvground__capacity_net"))
        .annotate(pvroof_net=Sum("pvroof__capacity_net"))
        .annotate(wind_net=Sum("windturbine__capacity_net"))
        .annotate(storage_net=Sum("storage__capacity_net"))
    )
