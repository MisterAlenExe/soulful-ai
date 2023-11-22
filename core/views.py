from django.views import View
from django.shortcuts import redirect
from django.views.generic import View


class IndexPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("chat/")
        else:
            return redirect("auth/login/")
