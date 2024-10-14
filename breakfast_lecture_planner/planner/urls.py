from django.urls import path

from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.Planner.as_view(), name='planner'),
    path('cabinet', views.CabinetView.as_view(), name='cabinet'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
    path(
        'contacts/',
        views.ContactsView.as_view(),
        name='contacts'),
    path(
        'faq/',
        views.FaqView.as_view(),
        name='faq'),
]
