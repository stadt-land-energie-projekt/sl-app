from django.urls import path
from django.views.generic import TemplateView

app_name = "users"
urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/map.html"), name="map"),
    path("details/", TemplateView.as_view(template_name="pages/details.html"), name="details"),
]
