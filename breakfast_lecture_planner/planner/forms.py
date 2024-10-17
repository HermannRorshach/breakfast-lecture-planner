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
            'date': forms.HiddenInput(),  # Используйте скрытое поле
        }

from django import forms
from .models import Feedback  # Убедитесь, что у вас есть модель Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваше сообщение'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email'}),
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
        }
        labels = {
            'name': 'Имя',
            'email': 'Email',
            'text': 'Сообщение',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('Поле не может быть пустым.')
        return text
