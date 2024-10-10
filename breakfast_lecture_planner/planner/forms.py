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

class WeekEventsForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = WeekEvents
        fields = ['image']  # Указано только редактируемое поле

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.day_events_formset = modelformset_factory(DayEvents, form=DayEventsForm, extra=7, can_delete=False)

    def is_valid(self):
        valid = super().is_valid()
        day_events = self.day_events_formset(self.data or None, self.files or None)
        return valid and day_events.is_valid()

    def save(self, commit=True):
        print("WeekEventsForm Data:", self.data)  # Вывод данных формы
        print("WeekEventsForm Files:", self.files)  # Вывод файлов формы

        week_event = super().save(commit=False)
        if commit:
            week_event.save()

        day_events = self.day_events_formset(self.data or None, self.files or None)

        # Проверяем валидность day_events_formset
        if day_events.is_valid():
            for form in day_events:
                day_event = form.save(commit=False)
                day_event.week_events = week_event
                day_event.save()
        else:
            print("DayEventsFormSet Errors:", day_events.errors)  # Вывод ошибок в day_events_formset

        return week_event