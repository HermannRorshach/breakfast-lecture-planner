from django import forms

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
        fields = ['lecturer', 'chef']
        widgets = {
            'lecturer': forms.Select(attrs={'class': 'form-control'}),
            'chef': forms.Select(attrs={'class': 'form-control'}),
        }


class WeekEventsForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = WeekEvents
        fields = ['image']

    def save(self, commit=True):
        week_event = super().save(commit=False)
        if commit:
            week_event.save()
        return week_event
