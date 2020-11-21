from django.contrib.auth.forms import UserCreationForm
from django import forms
from users.models import Account
from django.contrib.auth.forms import PasswordResetForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Account
        fields = ["name", "email", "password1", "password2"]


class EditAccountForm(forms.Form):
    name = forms.CharField(max_length=40)
    email = forms.EmailField(help_text='If you change your email you will be logged out to confirm it .')