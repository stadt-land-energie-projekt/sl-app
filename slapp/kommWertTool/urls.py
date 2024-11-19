from django.urls import path, re_path
from django.views.static import serve
from pathlib import Path
from . import views

app_name = 'kommWertTool'

BASE_DIR = Path(__file__).resolve().parent.parent
PLOTS_DIR = BASE_DIR / 'kommWertTool' / 'tmp' / 'chart'

urlpatterns = [
    path('', views.index, name='index'),
    path('added_value_results/', views.submit, name='submit'),
    #path('plots/<str:filename>/', views.send_plot, name='sendplot'),
    path("added_value/", views.index, name="added_value"),
    path('chart_data/<str:chart_type>/', views.check_charts_data, name='chart_data'),

]
