from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from markdown import markdown

from .forms import ImageUploadForm, LunchParticipantForm, PostForm
from .models import Image, Post


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


from datetime import datetime

from django.utils.html import format_html


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
        current_day_found = False
        saturday_found = False

        # Получаем URL для регистрации
        registration_url = reverse("planner:lunch_register")

        for line in lines:
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
                    f'{line.replace("-", "").strip()}'
                    f'</div>'
                )
                highlighted_lines.append(highlighted_line)
                current_day_found = True
            else:
                highlighted_lines.append(line)

            # Обрабатываем строку с "Šeštadienis"


        # Соединяем строки обратно в один текст
        highlighted_content = "\n".join(highlighted_lines)

        context['content'] = markdown(highlighted_content)
        context['title'] = "Tvarkaraštis"
        context['image'] = post.image
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
    template_name = 'planner/lunch_registration.html'

    def get(self, request):
        form = LunchParticipantForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LunchParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('planner:lunch_success')
        return render(request, self.template_name, {'form': form})


class LunchSuccessView(View):
    template_name = 'planner/success.html'

    def get(self, request):
        return render(request, self.template_name)