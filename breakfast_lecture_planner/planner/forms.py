from django import forms
from .models import Lecturer, Chef, DayEvents

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
