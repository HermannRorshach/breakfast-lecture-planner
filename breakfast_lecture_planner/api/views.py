from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from planner.models import Feedback, LunchParticipant
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Task
from .serializers import (FeedbackSerializer, LunchParticipantSerializer,
                          TaskSerializer, UserSerializer)


# Вьюсет, собранный из миксинов, который может только возвращать
# и удалять объекты, но не может их создавать, изменять и удалять
class CreateListRetrieveDestroyViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    pass


# Наследуемся от вьюсета, собранного из миксинов
class LunchParticipantViewSet(CreateListRetrieveDestroyViewSet):
    serializer_class = LunchParticipantSerializer

    def get_queryset(self):
        one_day_ago = timezone.now() - timedelta(days=1)
        return LunchParticipant.objects.filter(date__gte=one_day_ago)


class FeedbackViewSet(CreateListRetrieveDestroyViewSet):
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        return Feedback.objects.all()


class TaskViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):

    queryset = Task.objects.filter(done=False)
    serializer_class = TaskSerializer


class UserViewSet(ListModelMixin, GenericViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
