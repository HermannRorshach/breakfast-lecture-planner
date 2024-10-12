from decouple import config
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('planner:cabinet')
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        return super().form_valid(form)
