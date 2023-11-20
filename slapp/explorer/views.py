from django.views.generic import TemplateView
from django_mapengine import views


class MapGLView(TemplateView, views.MapEngineMixin):
    template_name = "pages/map.html"
    extra_context = {}
