# users/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def clean_confirm_password(self):
        password1 = self.cleaned_data.get("password1")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password1 != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return confirm_password


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["email", "password"]

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise forms.ValidationError("Invalid email or password.")

        return super(UserLoginForm, self).clean()
