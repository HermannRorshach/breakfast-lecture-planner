# from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import UserCreationForm

# User = get_user_model()


# class CreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ('first_name', 'last_name', 'username', 'email')


from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "groups", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.groups.set(self.cleaned_data["groups"])
        return user


class CustomUserEditForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "groups")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.groups.set(self.cleaned_data["groups"])
        return user
