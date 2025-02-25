from django.urls import path, re_path
from django.views.static import serve
from pathlib import Path
from . import views

app_name = 'kommWertTool'

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    path('', views.index, name='index'),
    path('added_value_results/', views.submit, name='submit'),
    path("added_value/", views.index, name="added_value"),
]
