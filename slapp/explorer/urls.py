"""Urls for explorer app."""

from django.urls import path

from slapp.explorer import views

app_name = "explorer"
urlpatterns = [
    path("start", views.start_page, name="home"),
    path("", views.MapGLView.as_view(), name="map"),
    path("details/", views.details_list, name="details"),
    path("details/csv/", views.details_csv, name="details-csv"),
    path("esm_mode/", views.choose_esm_mode, name="esm_mode"),
    path("parameters_variation/", views.optimization_parameters, name="parameters_variation"),
    path("results_variation/", views.optimization_results, name="results_variation"),
    path("results_robustness/", views.robustness, name="results_robustness"),
    path("parameters_robustness/", views.robustness_parameters, name="parameters_robustness"),
    path("added_value/", views.added_value, name="added_value"),
]

htmx_urlpatterns = [
    path("search-municipality/", views.search_municipality, name="search-municipality"),
    path("wizard-next/", views.next_menu_tab, name="wizard-next-step"),
    path("wizard-previous/", views.previous_menu_tab, name="wizard-previous-step"),
    path("esm-choice/<int:tab_id>", views.esm_choice, name="esm_choice"),
]

urlpatterns += htmx_urlpatterns
