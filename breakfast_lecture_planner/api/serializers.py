from django.contrib.auth import get_user_model
from planner.models import Feedback, LunchParticipant
from rest_framework.serializers import CharField, DateField, ModelSerializer

from .models import Task


class LunchParticipantSerializer(ModelSerializer):
    date = DateField(required=False)  # Сделаем поле date необязательным
    comment = CharField(
        required=False, allow_blank=True
    )  # Сделаем поле comment необязательным

    class Meta:
        model = LunchParticipant
        fields = "__all__"


class FeedbackSerializer(ModelSerializer):

    class Meta:
        model = Feedback
        fields = "__all__"


class TaskSerializer(ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"


class UserSerializer(ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ["email"]
