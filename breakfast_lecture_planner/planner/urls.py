from django.urls import path

from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.Planner.as_view(), name='planner'),
    path('cabinet', views.DayEventsCreateView.as_view(), name='cabinet'),
    path(
        'create_week_events',
        views.WeekEventsCreateView.as_view(),
        name='create_week_events'),
    path(
        'week/<int:pk>/edit/',
        views.WeekEventsUpdateView.as_view(),
        name='week_edit'),
    path(
        'weeks/',
        views.WeekEventsListView.as_view(),
        name='week_events_list'),
    path(
        'weeks/<int:pk>/',
        views.WeekEventsDetailView.as_view(),
        name='week_detail'),
    path(
        'lecturers/',
        views.LecturerListView.as_view(),
        name='lecturers_list'),
    path(
        'lecturers/add/',
        views.LecturerCreateView.as_view(),
        name='add_lecturer'),
    path(
        'lecturers/edit/<int:pk>/',
        views.LecturerUpdateView.as_view(),
        name='edit_lecturer'),
    path(
        'lecturers/delete/<int:pk>/',
        views.LecturerDeleteView.as_view(),
        name='delete_lecturer'),
    path(
        'chefs/',
        views.ChefListView.as_view(),
        name='chefs_list'),
    path(
        'chefs/add/',
        views.ChefCreateView.as_view(),
        name='add_chef'),
    path(
        'chefs/edit/<int:pk>/',
        views.ChefUpdateView.as_view(),
        name='edit_chef'),
    path(
        'chefs/delete/<int:pk>/',
        views.ChefDeleteView.as_view(),
        name='delete_chef'),
    path(
        'contacts/',
        views.ContactsView.as_view(),
        name='contacts'),
    path(
        'faq/',
        views.FaqView.as_view(),
        name='faq'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
]
