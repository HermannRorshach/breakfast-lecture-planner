from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView
from django.views.generic.edit import CreateView, DeleteView

from .forms import CustomUserCreationForm


def superuser_required(function):
    return user_passes_test(lambda u: u.is_superuser)(function)


class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('planner:cabinet')
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        return super().form_valid(form)


@method_decorator(superuser_required, name='dispatch')
class UserCreateView(CreateView):
    model = get_user_model()
    template_name = 'planner/add_person.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:user_list')
    extra_context = {'role': 'администратора'}

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)


@method_decorator(superuser_required, name='dispatch')
class UserListView(ListView):
    model = get_user_model()
    template_name = 'planner/persons_list.html'
    context_object_name = 'persons'
    extra_context = {
        'role_singular': 'Администратора',
        'role_plural': 'Администраторов',
        'path_delete': 'users:user_delete',
        'path_add_person': 'users:user_add',
        }


@method_decorator(superuser_required, name='dispatch')
class UserDeleteView(DeleteView):
    model = get_user_model()
    template_name = 'planner/delete_person.html'
    success_url = reverse_lazy('users:user_list')
    extra_context = {'role': 'администратора', 'path': 'users:user_list'}