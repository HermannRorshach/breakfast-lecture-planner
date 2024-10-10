from datetime import datetime

from calendar_utils.utils import get_next_week_number, get_start_and_end_dates
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ChefForm, DayEventsForm, LecturerForm, WeekEventsForm
from .models import Chef, DayEvents, Lecturer, WeekEvents
from django.views import View
from django.shortcuts import render, redirect


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

from django.forms import modelformset_factory

class WeekEventsCreateView(CreateView):
    model = WeekEvents
    form_class = WeekEventsForm
    template_name = 'planner/create_week_events.html'
    success_url = reverse_lazy('planner:planner')

    def form_valid(self, form):
        week_event = form.save()

        # Получаем day_events_formset из контекста
        day_events_formset = self.get_day_events_formset()
        for day_form in day_events_formset:
            if day_form.is_valid():
                day_event = day_form.save(commit=False)
                day_event.week_events = week_event
                day_event.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['day_events_formset'] = self.get_day_events_formset(self.request.POST, self.request.FILES)
        else:
            context['day_events_formset'] = self.get_day_events_formset()
        return context

    def get_day_events_formset(self, data=None, files=None):
        if data or files:
            # Если есть данные (POST-запрос), используем переданные данные
            return modelformset_factory(DayEvents, form=DayEventsForm, extra=2, can_delete=False)(data, files)
        else:
            # При GET-запросе возвращаем пустой queryset
            return modelformset_factory(DayEvents, form=DayEventsForm, extra=2, can_delete=False)(queryset=DayEvents.objects.none())
