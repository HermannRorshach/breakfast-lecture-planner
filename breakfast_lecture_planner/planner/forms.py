from datetime import datetime, time

from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from .models import Feedback, Image, LunchParticipant, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "full-width full-height"}),
            "content": forms.Textarea(attrs={"class": "full-width full-height"}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget.attrs.update(
            {
                "rows": 50,  # Задайте нужное количество строк
                "cols": 80,  # (необязательно) Задайте нужное количество столбцов
            }
        )


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["image"]


class LunchParticipantForm(forms.ModelForm):
    # Скрытое от пользователей поле, предназначенное для заполнения роботами
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Jūsų telefono numeris", "style": "opacity:0;"}
        ),
    )

    # Добавляем reCAPTCHA v3
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = ""
        self.fields["portions"].initial = ""
        self.fields["portions"].choices = [("", "Pasirinkite porcijų skaičių")] + list(
            self.fields["portions"].choices
        )

    def clean(self):
        cleaned_data = super().clean()
        # Защита от спама роботов - проверка заполнения скрытого поля
        if "phone" in cleaned_data and cleaned_data["phone"]:
            print("Форму отравляет робот")
            cleaned_data.pop("phone")
            cleaned_data["robot"] = True
        # Логика вычисления даты
        # now = datetime.strptime("14.12.24 23:59:59", "%d.%m.%y %H:%M:%S")
        now = datetime.now()
        current_weekday = now.weekday()

        if current_weekday == 4 and now.time() > time(17, 0) or (current_weekday == 5):
            cleaned_data["error_message"] = "Registration is over"
        print(cleaned_data)
        return cleaned_data

    class Meta:
        model = LunchParticipant
        fields = [
            "phone",
            "name",
            "email",
            "portions",
            "comment",
        ]  # Поле date исключено
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Komentaras"}),
            "email": forms.EmailInput(
                attrs={"placeholder": "Jusu el. paštas. Privalomas langelis"}
            ),
            "name": forms.TextInput(attrs={"placeholder": "Jusu vardas"}),
            "portions": forms.Select(attrs={"style": "color: #757575;"}),
        }


class FeedbackForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Jūsų telefono numeris", "style": "opacity:0;"}
        ),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = ""

    class Meta:
        model = Feedback
        fields = ["phone", "name", "email", "text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "placeholder": "Žinutė"}),
            "email": forms.EmailInput(
                attrs={"placeholder": "Jusu el. paštas. Privalomas langelis"}
            ),
            "name": forms.TextInput(attrs={"placeholder": "Jusu vardas"}),
        }
        labels = {
            "phone": "Номер телефона",
            "name": "Имя",
            "email": "Email",
            "text": "Сообщение",
        }

    def clean(self):
        cleaned_data = super().clean()
        # Защита от спама роботов - проверка заполнения скрытого поля
        if "phone" in cleaned_data and cleaned_data["phone"]:
            print("Форму отравляет робот")
            cleaned_data.pop("phone")
            cleaned_data["robot"] = True
        print(cleaned_data)
        return cleaned_data

    def clean_text(self):
        text = self.cleaned_data.get("text")
        if not text:
            raise forms.ValidationError("Поле не может быть пустым.")
        return text


from django import forms

from .models import Text


class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ["title", "text"]
