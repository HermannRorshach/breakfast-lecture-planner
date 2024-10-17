from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from markdown import markdown

from .forms import ImageUploadForm, LunchParticipantForm, PostForm
from .models import Image, LunchParticipant, Post


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
class CabinetView(View):
    template_name = 'planner/cabinet.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class Planner(DetailView):
    model = Post
    template_name = 'planner/post.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=12)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Получаем текущий день недели на литовском
        days_of_week = [
            "Pirmadienis",  # Понедельник
            "Antradienis",  # Вторник
            "Trečiadienis", # Среда
            "Ketvirtadienis", # Четверг
            "Penktadienis", # Пятница
            "Šeštadienis",  # Суббота
            "Sekmadienis"   # Воскресенье
        ]
        current_day = days_of_week[datetime.now().weekday()]

        # Разделяем контент на строки
        lines = post.content.splitlines()

        # Обрамляем строку с текущим днем и добавляем ссылку только для первой недели
        highlighted_lines = []
        user_content_lines = []
        current_day_found = False
        saturday_found = False
        data = {'not_schedule_text': []}
        key = None

        # Получаем URL для регистрации
        registration_url = reverse("planner:lunch_register")

        for line in lines:
            if "savaitė" in line:
                if key:
                    data[key].extend(highlighted_lines)
                    user_content_lines.extend(highlighted_lines)
                    highlighted_lines = []
                key = line
                data[key] = []
            if key in data:
                if line == key:
                    continue
                if "Šeštadienis" in line and not saturday_found:
                    path = '{% url "planner:lunch_register" %}'
                    registration_link = (
                        '<span style="color: red; font-weight: bold;">'
                        f'<a href="{registration_url}">Registracija</a>'
                        '</span>'
                    )
                    line = line.replace(line, f"{line} {registration_link}")
                    saturday_found = True
                # Обрабатываем строку с текущим днем
                if current_day in line and not current_day_found:
                    highlighted_line = (
                        f'<div style="border-top: 2px solid red; border-bottom: 2px solid red; margin: 10px 0; padding: 10px; width: 430px;">'
                        f'<h6>{line.replace("#", "").strip()}</h6>'
                        f'</div>'
                    )
                    highlighted_lines.append(highlighted_line)
                    current_day_found = True
                else:
                    highlighted_lines.append(line)
            else:
                data["not_schedule_text"].append(line)
        data[key].extend(highlighted_lines)
        user_content_lines.extend(highlighted_lines)

        # Соединяем строки обратно в один текст
        highlighted_content = "\n".join(user_content_lines)

        context['content'] = markdown(highlighted_content)
        context['title'] = "Tvarkaraštis"
        context['image'] = post.image

        not_schedule_text = data['not_schedule_text']
        del data['not_schedule_text']


        data = {
            markdown(key): markdown("\n".join(value)) if isinstance(value, list) else markdown(value)
            for key, value in data.items()
        }

        if not_schedule_text:  # Проверяем, что значение не пустое
            data['not_schedule_text'] = markdown("\n".join(not_schedule_text))

        context['data'] = data
        return context



@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'planner/post_form.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            self.object = form.save()
            return JsonResponse({'content': markdown(self.object.content)})

        return JsonResponse({'error': 'Invalid form'}, status=400)


class ImageListView(View):
    def get(self, request):
        images = Image.objects.all()  # Получаем все изображения
        context = {
            'images': images
        }
        return render(request, 'planner/image_list.html', context)


class ImageUploadView(View):
    def get(self, request):
        form = ImageUploadForm()
        return render(request, 'planner/image_upload.html', {'form': form})

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('planner:image_list')  # Перенаправление на страницу со списком изображений
        return render(request, 'planner/image_upload.html', {'form': form})


class DeleteImageView(View):
    def get(self, request, image_id):
        image = get_object_or_404(Image, id=image_id)
        image.delete()
        return redirect('planner:image_list')


class AddToHomeView(View):
    def get(self, request, image_id):
        image = get_object_or_404(Image, id=image_id)
        post = get_object_or_404(Post, pk=12)  # Получаем пост с pk=12
        post.image = image  # Устанавливаем изображение
        post.save()  # Сохраняем изменения
        return JsonResponse({'success': True, 'message': 'Изображение добавлено на главную!'})



class LunchRegistrationView(View):
    template_name = 'planner/registration_or_feedback.html'

    def get(self, request):
        # Получаем сегодняшнюю дату
        today = datetime.now()
        # Находим ближайшую субботу
        days_ahead = 5 - today.weekday()  # Суббота - 5-й день недели
        if days_ahead < 0:  # Если сегодня уже суббота или позже
            days_ahead += 7
        nearest_saturday = today + timedelta(days=days_ahead)

        form = LunchParticipantForm(initial={'date': nearest_saturday.date()})  # Устанавливаем начальное значение
        return render(request, self.template_name, {'form': form, 'title': 'Регистрация на обед'})

    def post(self, request):
        form = LunchParticipantForm(request.POST)
        if form.is_valid():
            lunch_participant = form.save(commit=False)  # Не сохраняем пока
            lunch_participant.date = form.cleaned_data['date'] or request.POST.get('date')  # Получаем дату
            lunch_participant.save()  # Теперь сохраняем
            return redirect('planner:lunch_success')
        return render(request, self.template_name, {'form': form, 'title': 'Регистрация на обед'})



class LunchSuccessView(View):
    template_name = 'planner/success.html'
    context = {
        'title': 'Вы зарегистрированы!',
        'action': 'регистрацию',
        'message': 'Вы успешно зарегистрировались на субботний обед!'}

    def get(self, request):
        return render(request, self.template_name, context=self.context)


class LunchParticipantListView(View):
    template_name = 'planner/lunch_participants.html'

    def get(self, request):
        one_day_ago = timezone.now() - timedelta(days=1)
        participants = LunchParticipant.objects.filter(date__gte=one_day_ago)
        context = {
            'participants': participants,
        }

        return render(request, self.template_name, context)


from django.views import View
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .forms import FeedbackForm  # Предположим, у вас есть форма FeedbackForm

class FeedbackView(View):
    template_name = 'planner/registration_or_feedback.html'  # Универсальное название

    def get_context_data(self):
        return {'title': 'Обратная связь'}

    def get(self, request):
        context = self.get_context_data()
        form = FeedbackForm()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.save()

            # Получаем всех зарегистрированных пользователей
            User = get_user_model()
            users = User.objects.values_list('email', flat=True)
            print(users)

            # Отправляем письмо всем пользователям
            subject = f"Обратная связь от {feedback.name}"
            message = f"Пользователь по имени {feedback.name} с email {feedback.email}, оставил обратную связь:\n{feedback.text}"
            from_email = feedback.email
            send_mail(subject, message, from_email, users)

            return redirect('planner:feedback_success')  # Перенаправление на страницу успеха

        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)

class FeedbackSuccessView(View):
    template_name = 'planner/success.html'
    context = {
        'title': 'Сообщение отправлено',
        'action': 'обратную связь',
        'message': 'Ваше сообщение успешно отправлено!\nПожалуйста, ожидайте ответа на email'
        }

    def get(self, request):
        return render(request, self.template_name, context=self.context)
