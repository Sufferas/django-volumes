from django.urls import path
from . import views


urlpatterns = [

    path('', views.list_immos, name="list-immo"),  # Dies wird die Hauptseite sein
    path('add_immo', views.create_project, name="add-immo"),

]