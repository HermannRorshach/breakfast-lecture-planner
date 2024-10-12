from datetime import datetime, timedelta

from calendar_utils.utils import (get_start_and_end_dates, get_weeks_in_year)
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ChefForm, DayEventsForm, LecturerForm, WeekEventsForm
from .models import Chef, DayEvents, Lecturer, WeekEvents
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class ContactsView(View):
    template_name = 'planner/contacts.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class FaqView(View):
    template_name = 'planner/FAQ.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class LecturerCreateView(CreateView):
    model = Lecturer
    form_class = LecturerForm
    template_name = 'planner/add_person.html'
    success_url = reverse_lazy('planner:lecturers_list')
    extra_context = {'role': 'Лектора'}


@method_decorator(login_required, name='dispatch')
class LecturerDeleteView(DeleteView):
    model = Lecturer
    template_name = 'planner/delete_person.html'
    success_url = reverse_lazy('planner:lecturers_list')
    extra_context = {'role': 'Лектора', 'path': 'planner:lecturers_list'}


@method_decorator(login_required, name='dispatch')
class LecturerUpdateView(UpdateView):
    model = Lecturer
    form_class = LecturerForm
    template_name = 'planner/edit_person.html'
    success_url = reverse_lazy('planner:lecturers_list')
    extra_context = {'role': 'Лектора'}


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class ChefCreateView(CreateView):
    model = Chef
    form_class = ChefForm
    template_name = 'planner/add_person.html'
    success_url = reverse_lazy('planner:chefs_list')
    extra_context = {'role': 'Повара'}


@method_decorator(login_required, name='dispatch')
class ChefDeleteView(DeleteView):
    model = Chef
    template_name = 'planner/delete_person.html'
    success_url = reverse_lazy('planner:chefs_list')
    extra_context = {'role': 'Повара', 'path': 'planner:chefs_list'}


@method_decorator(login_required, name='dispatch')
class ChefUpdateView(UpdateView):
    model = Chef
    form_class = ChefForm
    template_name = 'planner/edit_person.html'
    success_url = reverse_lazy('planner:chefs_list')
    extra_context = {'role': 'Повара'}


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class DayEventsCreateView(CreateView):
    model = DayEvents
    form_class = DayEventsForm
    template_name = 'planner/cabinet.html'
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


@method_decorator(login_required, name='dispatch')
class WeekEventsCreateView(CreateView):
    model = WeekEvents
    form_class = WeekEventsForm
    template_name = 'planner/create_week_events.html'
    success_url = reverse_lazy('planner:week_events_list')

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
                year += 1  # Увеличиваем год на 1
        else:
            year = datetime.today().year
            current_date = datetime.today()
            next_week_number = (
                current_date - datetime(current_date.year, 1, 1)
                ).days // 7 + 1

        # Вычисляем даты начала и конца недели
        start_date, end_date = get_start_and_end_dates(next_week_number, year)

        context.update({
            'week_number': next_week_number,
            'year': year,
            'start_date': start_date,
            'end_date': end_date,
            'days_of_week': (
                'Понедельник', 'Вторник', 'Среда', 'Четверг',
                'Пятница', 'Суббота', 'Воскресенье'),
            'day_events_formset': self.get_day_events_formset(),
        })
        return context

    def form_valid(self, form):
        week_event = form.save(commit=False)

        # Получаем данные из контекста
        week_event.week_number = self.request.POST.get('week_number') or self.kwargs.get('week_number')
        week_event.year = self.request.POST.get('year') or self.kwargs.get('year')
        week_event.start_date = datetime.strptime(self.request.POST.get('start_date'), '%Y-%m-%d')
        week_event.end_date = datetime.strptime(self.request.POST.get('end_date'), '%Y-%m-%d')

        week_event.save()  # Сохраняем week_event в базе данных

        # Обрабатываем day_events_formset
        day_events_formset = self.get_day_events_formset(self.request.POST)

        if day_events_formset.is_valid():
            for index, day_form in enumerate(day_events_formset):
                lecturer = day_form.cleaned_data.get('lecturer')
                chef = day_form.cleaned_data.get('chef')
                # Создаем или обновляем запись
                day_event = day_form.save(commit=False)
                day_event.week_events = week_event
                day_event.date = week_event.start_date + timedelta(days=index)
                day_event.save()

        return super().form_valid(form)

    def get_day_events_formset(self, data=None, files=None):
        return modelformset_factory(
            DayEvents, form=DayEventsForm, extra=7, can_delete=False)(
            data, files, queryset=DayEvents.objects.none(
            ) if data is None else None
        )


@method_decorator(login_required, name='dispatch')
class WeekEventsListView(ListView):
    model = WeekEvents
    template_name = 'planner/week_events_list.html'
    context_object_name = 'week_events'
    paginate_by = 52

    def get_queryset(self):
        return WeekEvents.objects.order_by('-year', '-week_number')


@method_decorator(login_required, name='dispatch')
class WeekEventsDetailView(DetailView):
    model = WeekEvents
    template_name = 'planner/week_event_detail.html'
    context_object_name = 'week_event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем связанные события на каждый день для отображения
        context['day_events'] = DayEvents.objects.filter(week_events=self.object)
        return context


@method_decorator(login_required, name='dispatch')
class WeekEventsUpdateView(UpdateView):
    model = WeekEvents
    form_class = WeekEventsForm
    template_name = 'planner/create_week_events.html'
    success_url = reverse_lazy('planner:week_events_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        week_event = self.object  # Текущая запись WeekEvents

        context.update({
            'week_number': week_event.week_number,
            'year': week_event.year,
            'start_date': week_event.start_date,
            'end_date': week_event.end_date,
            'days_of_week': (
                'Понедельник', 'Вторник', 'Среда', 'Четверг',
                'Пятница', 'Суббота', 'Воскресенье'),
            'day_events_formset': self.get_day_events_formset(),
        })
        return context



    def form_valid(self, form):
        week_event = form.save(commit=False)

        # Получаем данные из контекста для обновления week_event
        week_event.start_date = datetime.strptime(self.request.POST.get('start_date'), '%Y-%m-%d')
        week_event.end_date = datetime.strptime(self.request.POST.get('end_date'), '%Y-%m-%d')

        week_event.save()  # Сохраняем изменения в базе данных

        # Обрабатываем day_events_formset
        day_events_formset = self.get_day_events_formset(self.request.POST)

        if day_events_formset.is_valid():
            for index, day_form in enumerate(day_events_formset):
                lecturer = day_form.cleaned_data.get('lecturer')
                chef = day_form.cleaned_data.get('chef')

                # Обновляем или создаем запись
                day_event = day_form.save(commit=False)
                day_event.week_events = week_event
                day_event.date = week_event.start_date + timedelta(days=index)

                day_event.save()

        return super().form_valid(form)

    def get_day_events_formset(self, data=None, files=None):
        queryset = DayEvents.objects.filter(week_events=self.object)

        # Количество дополнительных пустых форм
        extra_forms = max(7 - queryset.count(), 0)

        return modelformset_factory(
            DayEvents, form=DayEventsForm, extra=extra_forms, can_delete=False
        )(data, files, queryset=queryset)


from django.views.generic import DetailView
from .models import Post
from markdown import markdown
from .forms import PostForm


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'planner/post_form.html'

    def get_success_url(self):
        return reverse_lazy('planner:post-detail', kwargs={'pk': self.object.pk})


class PostDetailView(DetailView):
    model = Post
    template_name = 'planner/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['content'] = markdown(post.content)
        return context


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'planner/post_form.html'

    def get_success_url(self):
        return reverse_lazy('planner:post-detail', kwargs={'pk': self.object.pk})