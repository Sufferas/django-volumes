from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('', views.list_immos, name="list-immo"),  # Dies wird die Hauptseite sein
    path('add_immo', views.create_project, name="add-immo"),
    path('delete_immo/<int:immo_id>/', views.delete_immo, name="delete-immo"),
    path('edit_immo/<int:immo_id>/', views.edit_immo, name="edit-immo"),
    path('delete_image/', views.delete_image, name="delete-image"),
    path('delete_dokument/', views.delete_dokument, name='delete-dokument'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('projects/', csrf_exempt(views.ProjectListView.as_view()), name='project-list'),
    path('project/<str:object_id>/<str:label>/', views.ProjectDetailView.as_view(), name='project-detail'),
]
