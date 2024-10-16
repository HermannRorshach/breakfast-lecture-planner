from django import forms

from .models import Image, LunchParticipant, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'full-width full-height'}),
            'content': forms.Textarea(attrs={'class': 'full-width full-height'}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'rows': 50,  # Задайте нужное количество строк
            'cols': 80   # (необязательно) Задайте нужное количество столбцов
        })


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']


class LunchParticipantForm(forms.ModelForm):
    class Meta:
        model = LunchParticipant
        fields = ['name', 'email', 'portions', 'comment', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Используем DateInput с типом 'date'
        }
