from django import forms
from .models import Post

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
