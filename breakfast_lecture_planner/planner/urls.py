from django.urls import path

from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.Planner.as_view(), name='planner'),
    path('add-data', views.DayEventsCreateView.as_view(), name='add_data'),
    path('lecturers/', views.LecturerListView.as_view(), name='lecturers_list'),
    path('lecturers/add/', views.LecturerCreateView.as_view(), name='add_lecturer'),
    path('lecturers/edit/<int:pk>/', views.LecturerUpdateView.as_view(), name='edit_lecturer'),
    path('lecturers/delete/<int:pk>/', views.LecturerDeleteView.as_view(), name='delete_lecturer'),
    path('chefs/', views.ChefListView.as_view(), name='chefs_list'),
    path('chefs/add/', views.ChefCreateView.as_view(), name='add_chef'),
    path('chefs/edit/<int:pk>/', views.ChefUpdateView.as_view(), name='edit_chef'),
    path('chefs/delete/<int:pk>/', views.ChefDeleteView.as_view(), name='delete_chef'),
]
