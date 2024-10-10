from calendar_utils.utils import get_next_week_number
from django import forms
from django.forms import modelformset_factory

from .models import Chef, DayEvents, Lecturer, WeekEvents


class LecturerForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ChefForm(forms.ModelForm):
    class Meta:
        model = Chef
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DayEventsForm(forms.ModelForm):
    class Meta:
        model = DayEvents
        fields = ['date', 'lecturer', 'chef']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lecturer': forms.Select(attrs={'class': 'form-control'}),
            'chef': forms.Select(attrs={'class': 'form-control'}),
        }

class WeekEventsForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = WeekEvents
        fields = ['image', 'week_number', 'year', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.day_events_formset = modelformset_factory(DayEvents, form=DayEventsForm, extra=2, can_delete=False)(
            self.data or None, self.files or None
        )


    def is_valid(self):
        valid = super().is_valid()
        day_events_valid = self.day_events_formset.is_valid()
        return valid and day_events_valid


    def save(self, commit=True):

        week_event = super().save(commit=False)
        if commit:
            week_event.save()

        day_events = self.day_events_formset

        if day_events.is_valid():
            for form in day_events:
                day_event = form.save(commit=False)
                day_event.week_events = week_event
                day_event.save()

        return week_event
