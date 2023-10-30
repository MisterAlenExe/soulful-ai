from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import FormView

from .forms import UserRegistrationForm, UserLoginForm


class PreventLoggedInUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/test-auth/")

        return super(PreventLoggedInUserMixin, self).dispatch(request, *args, **kwargs)


class UserRegisterView(PreventLoggedInUserMixin, FormView):
    template_name = "user/register.html"
    form_class = UserRegistrationForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "You have successfully registered")
        return super(UserRegisterView, self).form_valid(form)


class UserLoginView(PreventLoggedInUserMixin, FormView):
    template_name = "user/login.html"
    form_class = UserLoginForm
    success_url = "/"

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, "You have successfully logged in")
        return super(UserLoginView, self).form_valid(form)
