from django.contrib import admin

from .models import Feedback, LunchParticipant


@admin.register(LunchParticipant)
class LunchParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "portions", "comment", "date", "registration_date")
    search_fields = ("name", "email")
    list_filter = ("date", "registration_date")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "text", "date")
    search_fields = ("name", "email", "text")
    list_filter = ("date",)
