from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ChefForm, DayEventsForm, LecturerForm
from .models import Chef, DayEvents, Lecturer


class LecturerCreateView(CreateView):
    model = Lecturer
    form_class = LecturerForm
    template_name = 'planner/add_person.html'
    success_url = reverse_lazy('planner:lecturers_list')
    extra_context = {'role': 'Лектора'}


class LecturerDeleteView(DeleteView):
    model = Lecturer
    template_name = 'planner/delete_person.html'
    success_url = reverse_lazy('planner:lecturers_list')
    extra_context = {'role': 'Лектора'}

class LecturerUpdateView(UpdateView):
    model = Lecturer
    form_class = LecturerForm
    template_name = 'planner/edit_person.html'
    success_url = reverse_lazy('planner:lecturers_list')
    extra_context = {'role': 'Лектора'}

class LecturerListView(ListView):
    model = Lecturer
    template_name = 'planner/persons_list.html'
    context_object_name = 'persons'
    extra_context = {
        'role_singular': 'Лектора',
        'role_plural': 'Лекторов',
        'path_edit': 'planner:edit_lecturer',
        'path_delete': 'planner:delete_lecturer',
        'path_add_person': 'planner:add_lecturer',
        }

class ChefCreateView(CreateView):
    model = Chef
    form_class = ChefForm
    template_name = 'planner/add_person.html'
    success_url = reverse_lazy('planner:chefs_list')
    extra_context = {'role': 'Повара'}

class ChefDeleteView(DeleteView):
    model = Chef
    template_name = 'planner/delete_person.html'
    success_url = reverse_lazy('planner:chefs_list')
    extra_context = {'role': 'Повара'}

class ChefUpdateView(UpdateView):
    model = Chef
    form_class = ChefForm
    template_name = 'planner/edit_person.html'
    success_url = reverse_lazy('planner:chefs_list')
    extra_context = {'role': 'Повара'}

class ChefListView(ListView):
    model = Chef
    template_name = 'planner/persons_list.html'
    context_object_name = 'persons'
    extra_context = {
        'role_singular': 'Повара',
        'role_plural': 'Поваров',
        'path_edit': 'planner:edit_chef',
        'path_delete': 'planner:delete_chef',
        'path_add_person': 'planner:add_chef',
        }

class DayEventsCreateView(CreateView):
    model = DayEvents
    form_class = DayEventsForm
    template_name = 'planner/add_data.html'
    success_url = reverse_lazy('planner:planner')

    def form_valid(self, form):
        # Логика перед сохранением данных, если необходимо
        return super().form_valid(form)


class Planner(ListView):
    model = DayEvents
    template_name = 'planner/day_events.html'
    context_object_name = 'objects'

    def get_queryset(self):
        # Ваш код для получения списка
        return DayEvents.objects.all()  # Или любой другой запрос

    def get(self, request, *args, **kwargs):
        self.extra_context = {'menu_items': ['item1', 'item2', 'item3']}  # Пример списка
        return super().get(request, *args, **kwargs)
