from django.views import View
from django.shortcuts import redirect
from django.views.generic import View, TemplateView


class IndexPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("chat/")
        else:
            return redirect("auth/login/")


class ProfilePageView(TemplateView):
    template_name = "core/profile.html"
