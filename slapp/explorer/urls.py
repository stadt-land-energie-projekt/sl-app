from django.urls import path
from django.views.generic import TemplateView

from slapp.explorer import views

app_name = "explorer"
urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/map.html"), name="map"),
    path("details/", views.details_list, name="details"),
    path("parameters/", TemplateView.as_view(template_name="pages/parameters.html"), name="parameters"),
    path("details/csv/", views.details_csv, name="details-csv"),
]

htmx_urlpatterns = [
    path("search-municipality/", views.search_municipality, name="search-municipality"),
]

urlpatterns += htmx_urlpatterns
