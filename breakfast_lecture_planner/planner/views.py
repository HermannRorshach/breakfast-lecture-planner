from datetime import datetime, timedelta

from calendar_utils.utils import (get_next_week_number,
                                  get_start_and_end_dates, get_weeks_in_year)
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ChefForm, DayEventsForm, LecturerForm, WeekEventsForm
from .models import Chef, DayEvents, Lecturer, WeekEvents


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
        return DayEvents.objects.all()

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'menu_items': ['item1', 'item2', 'item3']}
        return super().get(request, *args, **kwargs)


class WeekEventsCreateView(CreateView):
    model = WeekEvents
    form_class = WeekEventsForm
    template_name = 'planner/create_week_events.html'
    success_url = reverse_lazy('planner:planner')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем последнюю запись в базе данных
        last_week_event = WeekEvents.objects.order_by(
            '-year', '-week_number').first()

        if last_week_event:
            year = last_week_event.year
            next_week_number = last_week_event.week_number + 1

            # Проверка на превышение количества недель в году
            if next_week_number > get_weeks_in_year(year):
                next_week_number = 1
        else:
            year = datetime.today().year
            next_week_number = 1

        # Вычисляем даты начала и конца недели
        start_date, end_date = get_start_and_end_dates(next_week_number, year)

        context.update({
            'week_number': next_week_number,
            'year': year,
            'start_date': start_date,
            'end_date': end_date,
            'day_events_formset': self.get_day_events_formset(),
        })
        return context

    def form_valid(self, form):
        # Сохраняем week_event
        week_event = form.save(commit=False)

        # Получаем данные из контекста
        week_event.week_number = self.request.POST.get(
            'week_number') or self.kwargs.get('week_number')
        week_event.year = self.request.POST.get(
            'year') or self.kwargs.get('year')
        week_event.start_date = datetime.strptime(
            self.request.POST.get('start_date'), '%Y-%m-%d')
        week_event.end_date = datetime.strptime(
            self.request.POST.get('end_date'), '%Y-%m-%d')

        week_event.save()  # Сохраняем week_event в базе данных

        # Обрабатываем day_events_formset
        day_events_formset = self.get_day_events_formset(self.request.POST)

        if day_events_formset.is_valid():
            for day_form in day_events_formset:
                day_event = day_form.save(commit=False)
                day_event.week_events = week_event
                day_event.date = week_event.start_date + timedelta(
                    days=day_events_formset.forms.index(day_form))
                day_event.save()

        return super().form_valid(form)

    def get_day_events_formset(self, data=None, files=None):
        return modelformset_factory(
            DayEvents, form=DayEventsForm, extra=2, can_delete=False)(
            data, files, queryset=DayEvents.objects.none(
            ) if data is None else None
        )
