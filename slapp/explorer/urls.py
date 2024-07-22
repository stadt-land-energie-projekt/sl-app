"""Urls for explorer app."""

from django.urls import path

from slapp.explorer import views

app_name = "explorer"
urlpatterns = [
    path("", views.MapGLView.as_view(), name="map"),
    path("details/", views.details_list, name="details"),
    path("details/csv/", views.details_csv, name="details-csv"),
    path("esm_mode/", views.choose_esm_mode, name="esm_mode"),
    path("parameters/", views.optimization_parameters, name="parameters"),
    path("results", views.optimization_results, name="results"),
    path("robustness", views.robustness, name="robustness"),
]

htmx_urlpatterns = [
    path("search-municipality/", views.search_municipality, name="search-municipality"),
]

urlpatterns += htmx_urlpatterns
