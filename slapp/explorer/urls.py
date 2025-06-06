"""Urls for explorer app."""

from django.urls import path

from slapp.explorer import views

app_name = "explorer"
urlpatterns = [
    path("", views.start_page, name="home"),
    path("map/", views.MapGLView.as_view(), name="map"),
    path("details/", views.details_list, name="details"),
    path("details/csv/", views.details_csv, name="details-csv"),
    path("esm_mode/", views.choose_esm_mode, name="esm_mode"),
    path("parameters_variation/", views.optimization_parameters, name="parameters_variation"),
    path("results_variation/", views.optimization_results, name="results_variation"),
    path("results_robustness/", views.robustness, name="results_robustness"),
    path("parameters_robustness/", views.robustness_parameters, name="parameters_robustness"),
    path("case_studies/", views.CaseStudies.as_view(), name="case_studies"),
    path("chart/all_charts", views.all_charts, name="all_charts"),
    path("esys_robust/", views.EsysRobust.as_view(), name="esys_robust"),
    path("results/", views.Results.as_view(), name="results"),
    path("chart/flow_chart/", views.flow_chart, name="flow_chart"),
    path("cost_capacity_chart/", views.cost_capacity_chart, name="cost_capacity_chart"),
    path("demand_chart/", views.demand_chart, name="demand_chart"),
    path("demand_capacity_chart/", views.demand_capacity_chart, name="demand_capacity_chart"),
    path("basic_charts/", views.basic_charts, name="basic_charts"),
    path("ranges/", views.ranges, name="ranges"),
]

htmx_urlpatterns = [
    path("load-municipalities/", views.load_municipalities, name="load_municipalities"),
    path("muns-to-banner/", views.muns_to_banner, name="muns_to_banner"),
    path("search-municipality/", views.search_municipality, name="search-municipality"),
    path("wizard-next/", views.next_menu_tab, name="wizard-next-step"),
    path("wizard-previous/", views.previous_menu_tab, name="wizard-previous-step"),
    path("esm-choice/<int:tab_id>", views.esm_choice, name="esm_choice"),
]

urlpatterns += htmx_urlpatterns
