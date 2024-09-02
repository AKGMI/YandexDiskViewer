from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download, name='download'),
    path('download_selected/', views.download_selected, name='download_selected'),
]
