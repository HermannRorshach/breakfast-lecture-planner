from django.conf import settings
from django.conf.urls.static import static
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
    path('images/', views.ImageListView.as_view(), name='image_list'),
    path('images/upload/', views.ImageUploadView.as_view(), name='image_upload'),
    path('images/add-to-home/<int:image_id>/', views.AddToHomeView.as_view(), name='add_to_home'),
    path('images/delete/<int:image_id>/', views.DeleteImageView.as_view(), name='delete_image'),
    path('lunch/register/', views.LunchRegistrationView.as_view(), name='lunch_register'),
    path('lunch/success/', views.LunchSuccessView.as_view(), name='lunch_success'),
    path('lunch/participants/', views.LunchParticipantListView.as_view(), name='lunch_participants'),
    path('feedback', views.FeedbackView.as_view(), name='feedback'),
    path('feedback/success/', views.FeedbackSuccessView.as_view(), name='feedback_success'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
