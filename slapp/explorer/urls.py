from django.urls import path
from django.views.generic import TemplateView

from slapp.explorer import views

app_name = "explorer"
urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/map.html"), name="map"),
    path("details/", views.MunicipalityListView.as_view(), name="details"),
]
