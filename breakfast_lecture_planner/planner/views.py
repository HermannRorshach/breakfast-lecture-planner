import html
import os
import re
from datetime import date, datetime, time, timedelta
from math import pi

import requests
from api.models import Task
from calendar_utils.utils import get_next_day_with_time
from decouple import config
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from dotenv import load_dotenv
from markdown import markdown

from .forms import (
    FeedbackForm,
    ImageUploadForm,
    LunchParticipantForm,
    MainPostEditorForm,
    PostForm,
)
from .models import Image, LunchParticipant, Post

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_EMAIL = config("ADMIN_EMAIL")
TELEGRAM_CHAT_IDS = list(map(int, os.getenv("TELEGRAM_CHAT_IDS", "").split(",")))


def is_admin(user):
    return user.groups.filter(name="Админ").exists()


class ContactsView(View):
    template_name = "planner/contacts.html"

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name="dispatch")
class FaqView(View):
    template_name = "planner/FAQ.html"

    def get(self, request):
        return render(request, self.template_name)


class CombinedView(DetailView):
    model = Post
    template_name = "planner/combined.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=12)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Получаем текущий день недели на литовском
        days_of_week = [
            "Pirmadienis",  # Понедельник
            "Antradienis",  # Вторник
            "Trečiadienis",  # Среда
            "Ketvirtadienis",  # Четверг
            "Penktadienis",  # Пятница
            "Šeštadienis",  # Суббота
            "Sekmadienis",  # Воскресенье
        ]
        local_today = timezone.localdate()
        current_day = days_of_week[local_today.weekday()]
        current_date_heading = f"{local_today.day} d. {current_day}"
        current_week_friday = local_today + timedelta(days=4 - local_today.weekday())
        current_friday_heading = f"{current_week_friday.day} d. Penktadienis"

        # Разделяем контент на строки
        lines = post.content.splitlines()
        is_ckeditor_html = bool(
            re.search(r"<h[1-6]\b", post.content, flags=re.IGNORECASE)
        )

        # Обрамляем строку с текущим днем и добавляем ссылку только для первой недели
        highlighted_lines = []
        user_content_lines = []
        data = {"not_schedule_text": []}
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
                highlighted_lines.append(line)
            else:
                data["not_schedule_text"].append(line)
        if key and key in data:
            data[key].extend(highlighted_lines)
            user_content_lines.extend(highlighted_lines)

        # Соединяем строки обратно в один текст
        highlighted_content = "\n".join(user_content_lines)

        context["title"] = "pagrindinis"
        context["content"] = markdown(
            post.content if is_ckeditor_html else highlighted_content
        )
        context["image"] = post.image

        not_schedule_text = data["not_schedule_text"]
        del data["not_schedule_text"]

        data = {
            markdown(key): (
                markdown("\n".join(value))
                if isinstance(value, list)
                else markdown(value)
            )
            for key, value in data.items()
        }
        if is_ckeditor_html:
            # HTML CKEditor не нужно повторно делить на недели как Markdown.
            # Иначе вся однострочная разметка становится ключом data, и шаблон
            # выводит её до того, как добавлены today и Registracija.
            data = {}

        # CKEditor может добавлять атрибуты и вложенные теги в заголовок.
        # Сравниваем только его текст, а сохранённое содержимое поста не меняем.
        heading_pattern = re.compile(r"<h6\b[^>]*>.*?</h6>", re.IGNORECASE | re.DOTALL)
        today_anchor_added = False
        registration_link_added = False
        registration_link = (
            '<span style="color: red; font-weight: bold;">'
            f'<a href="{registration_url}" style="color: red;">Registracija</a>'
            "</span>"
        )

        def decorate_schedule_heading(match):
            nonlocal today_anchor_added, registration_link_added

            heading_html = match.group(0)
            heading_text = re.sub(r"<[^>]+>", "", heading_html)
            heading_text = " ".join(html.unescape(heading_text).split())
            heading_without_registration = re.sub(
                r"\s+Registracija\s*$", "", heading_text, flags=re.IGNORECASE
            )

            if (
                not registration_link_added
                and heading_without_registration.casefold()
                == current_friday_heading.casefold()
            ):
                if heading_text == heading_without_registration:
                    heading_html = re.sub(
                        r"</h6>\s*$",
                        f" {registration_link}</h6>",
                        heading_html,
                        count=1,
                        flags=re.IGNORECASE,
                    )
                registration_link_added = True

            if (
                not today_anchor_added
                and heading_without_registration.casefold()
                == current_date_heading.casefold()
            ):
                heading_html = f'<div id="today">{heading_html}</div>'
                today_anchor_added = True

            return heading_html

        # CKEditor обычно сохраняет весь HTML без переводов строк. В этом случае
        # старый разбор по неделям оставляет data пустым, и шаблон выводит content.
        context["content"] = heading_pattern.sub(
            decorate_schedule_heading, context["content"]
        )

        for key, value in data.items():
            data[key] = heading_pattern.sub(decorate_schedule_heading, value)

        if not_schedule_text:  # Проверяем, что значение не пустое
            data["not_schedule_text"] = markdown("\n".join(not_schedule_text))

        context["data"] = data

        countdown = [
            {"value": 0, "label": "days", "degrees": 0},
            {"value": 0, "label": "hours", "degrees": 0},
            {"value": 0, "label": "min", "degrees": 0},
            {"value": 0, "label": "sec", "degrees": 0},
        ]

        now = datetime.strptime("13.12.24 17:59:59", "%d.%m.%y %H:%M:%S")
        now = datetime.now()
        current_weekday = now.weekday()
        today = datetime.strptime("13.12.24", "%d.%m.%y")
        today = date.today()

        if not (
            current_weekday == 4 and now.time() > time(17, 0) or (current_weekday == 5)
        ):

            context.update(
                {
                    "target_day": 4,
                    "target_time": (17, 0, 0),
                    "current_weekday": current_weekday,
                    "current_date": today,
                    "now": now,
                }
            )

            next_friday_17 = get_next_day_with_time(context)
            # print(next_friday_17, type(next_friday_17))
            context["next_friday_17"] = (
                next_friday_17.year,
                next_friday_17.month,
                next_friday_17.day,
                next_friday_17.hour,
                next_friday_17.minute,
                next_friday_17.second,
            )

            riga_now = timezone.localtime(timezone.now())
            print("riga_now =", riga_now)
            context["now_tuple"] = (
                riga_now.year,
                riga_now.month,
                riga_now.day,
                riga_now.hour,
                riga_now.minute,
                riga_now.second,
            )
            # context["now_tuple"] = (2025, 3, 13, 2, 59, 45)
            # context["now_tuple"] = (2025, 3, 13, 16, 58, 55)
            delta = next_friday_17 - now
            print(delta, type(delta))
            print(delta.days, delta.seconds)
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60

        #     countdown[0]["value"] = days
        #     countdown[0]["degrees"] = 360 - (days / 7 * 360)
        #     print('Угол дня countdown[0]["degrees"] =', countdown[0]["degrees"])

        #     for index, time_element in enumerate(countdown[1:]):

        #         value = [hours, minutes, seconds][index]
        #         print(value)
        #         countdown[index + 1]["value"] = value
        #         countdown[index + 1]["degrees"] = 360 - (value / 60 * 360)

        # # Радиус окружности
        # radius = 41
        # # Длина окружности (2 * π * радиус)
        # circumference = 2 * pi * radius

        # # Добавляем в каждый элемент списка расчёт значения для stroke-dasharray
        # for unit in countdown:
        #     # Рассчитываем длину дуги для текущего прогресса
        #     unit['stroke_dasharray'] = (unit['degrees'] / 360) * circumference

        # Отправляем в контекст
        context["countdown"] = countdown
        # Добавляем список групп, которым будет разрешено редактирование страницы
        context["allowed_groups"] = ["Админ"]
        if self.request.user.is_authenticated and is_admin(self.request.user):
            context["editor_form"] = MainPostEditorForm(instance=post)
            context["unified_editor"] = True
        print("/n---------------/n")
        # print(context["now_tuple"])
        print("/n------------/n")
        print("/n---------------/n")
        print(context.keys())
        print("/n------------/n")
        return context


class Main(View):
    template_name = "planner/main.html"

    def get(self, request):
        countdown = [
            {"value": 0, "label": "days", "degrees": 0},
            {"value": 0, "label": "hours", "degrees": 0},
            {"value": 0, "label": "min", "degrees": 0},
            {"value": 0, "label": "sec", "degrees": 0},
        ]

        now = datetime.strptime("13.12.24 17:59:59", "%d.%m.%y %H:%M:%S")
        now = datetime.now()
        current_weekday = now.weekday()
        today = datetime.strptime("13.12.24", "%d.%m.%y")
        today = date.today()

        if not (
            current_weekday == 4 and now.time() > time(17, 0) or (current_weekday == 5)
        ):

            context = {
                "target_day": 4,
                "target_time": (17, 0, 0),
                "current_weekday": current_weekday,
                "current_date": today,
                "now": now,
            }
            next_friday_17 = get_next_day_with_time(context)
            print(next_friday_17)
            delta = next_friday_17 - now
            print(delta, type(delta))
            print(delta.days, delta.seconds)
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60

            countdown[0]["value"] = days
            countdown[0]["degrees"] = 360 - (days / 7 * 360)

            for index, time_element in enumerate(countdown[1:]):

                value = [hours, minutes, seconds][index]
                print(value)
                countdown[index + 1]["value"] = value
                countdown[index + 1]["degrees"] = 360 - (value / 60 * 360)

        # Радиус окружности
        radius = 41
        # Длина окружности (2 * π * радиус)
        circumference = 2 * pi * radius

        # Добавляем в каждый элемент списка расчёт значения для stroke-dasharray
        for unit in countdown:
            # Рассчитываем длину дуги для текущего прогресса
            unit["stroke_dasharray"] = (unit["degrees"] / 360) * circumference

        # Отправляем в контекст
        context = {
            "countdown": countdown,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(is_admin), name="dispatch")
class CabinetView(View):
    template_name = "planner/cabinet.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class Planner(DetailView):
    model = Post
    template_name = "planner/post.html"

    def get(self, request, *args, **kwargs):
        return redirect("planner:new")

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=12)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Получаем текущий день недели на литовском
        days_of_week = [
            "Pirmadienis",  # Понедельник
            "Antradienis",  # Вторник
            "Trečiadienis",  # Среда
            "Ketvirtadienis",  # Четверг
            "Penktadienis",  # Пятница
            "Šeštadienis",  # Суббота
            "Sekmadienis",  # Воскресенье
        ]
        current_day = days_of_week[datetime.now().weekday()]

        # Разделяем контент на строки
        lines = post.content.splitlines()

        # Обрамляем строку с текущим днем и добавляем ссылку только для первой недели
        highlighted_lines = []
        user_content_lines = []
        current_day_found = False
        saturday_found = False
        data = {"not_schedule_text": []}
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
                        "</span>"
                    )
                    line = line.replace(line, f"{line} {registration_link}")
                    saturday_found = True
                # Обрабатываем строку с текущим днем
                if current_day in line and not current_day_found:
                    highlighted_line = (
                        f'<div id="today"">'
                        f'<h6>{line.replace("#", "").strip()}</h6>'
                        f"</div>"
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

        context["content"] = markdown(highlighted_content)
        context["title"] = "Tvarkaraštis"
        context["image"] = post.image

        not_schedule_text = data["not_schedule_text"]
        del data["not_schedule_text"]

        data = {
            markdown(key): (
                markdown("\n".join(value))
                if isinstance(value, list)
                else markdown(value)
            )
            for key, value in data.items()
        }

        if not_schedule_text:  # Проверяем, что значение не пустое
            data["not_schedule_text"] = markdown("\n".join(not_schedule_text))

        context["data"] = data
        context["allowed_groups"] = ["Админ"]
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(is_admin), name="dispatch")
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "planner/post_form.html"

    def get_success_url(self):
        return reverse_lazy("planner:post-detail", kwargs={"pk": self.object.pk})


class PostDetailView(DetailView):
    model = Post
    template_name = "planner/combined.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["content"] = markdown(post.content)
        countdown = [
            {"value": 0, "label": "days", "degrees": 0},
            {"value": 0, "label": "hours", "degrees": 0},
            {"value": 0, "label": "min", "degrees": 0},
            {"value": 0, "label": "sec", "degrees": 0},
        ]

        now = datetime.strptime("13.12.24 17:59:59", "%d.%m.%y %H:%M:%S")
        now = datetime.now()
        current_weekday = now.weekday()
        today = datetime.strptime("13.12.24", "%d.%m.%y")
        today = date.today()

        if not (
            current_weekday == 4 and now.time() > time(17, 0) or (current_weekday == 5)
        ):

            context.update(
                {
                    "target_day": 4,
                    "target_time": (17, 0, 0),
                    "current_weekday": current_weekday,
                    "current_date": today,
                    "now": now,
                }
            )

            next_friday_17 = get_next_day_with_time(context)
            context["next_friday_17"] = (
                next_friday_17.year,
                next_friday_17.month,
                next_friday_17.day,
                next_friday_17.hour,
                next_friday_17.minute,
                next_friday_17.second,
            )

            riga_now = timezone.localtime(timezone.now())
            context["now_tuple"] = (
                riga_now.year,
                riga_now.month,
                riga_now.day,
                riga_now.hour,
                riga_now.minute,
                riga_now.second,
            )

        # Отправляем в контекст
        context["countdown"] = countdown
        context["allowed_groups"] = ["Админ"]
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(is_admin), name="dispatch")
class PostUpdateView(UpdateView):
    model = Post
    form_class = MainPostEditorForm
    template_name = "planner/post_form.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            self.object = form.save()
            return JsonResponse({"content": markdown(self.object.content)})

        return JsonResponse({"error": "Invalid form"}, status=400)


class NuarodosView(PostDetailView):
    def get_object(self, queryset=None):
        # Возвращаем объект с pk=15
        return Post.objects.get(pk=15)


class VaishnavaCalendar(PostDetailView):
    extra_context = {"title": "Vaišnavų kalendorius"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=14)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allowed_groups"] = ["Админ", "Энтузиаст"]
        return context


class VaishnavaEtiquette(PostDetailView):
    extra_context = {"title": "Vaišnavų etiketas"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=20)


class RenovationWork(PostDetailView):
    extra_context = {"title": "Šventyklos remonto darbai"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=21)


class IsdView(PostDetailView):
    extra_context = {"title": "isd"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=22)


class CleanlinessStandards(PostDetailView):
    extra_context = {"title": "Švaros standartai"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=23)


class Philosophy(PostDetailView):
    extra_context = {"title": "filosofija"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=24)


class Practice(PostDetailView):
    extra_context = {"title": "praktika"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=25)


@method_decorator(login_required, name="dispatch")
class ArchiveView(PostDetailView):
    def get_object(self, queryset=None):
        return Post.objects.get(pk=17)


class ImageListView(View):
    def get(self, request):
        images = Image.objects.all()  # Получаем все изображения
        context = {"images": images}
        return render(request, "planner/image_list.html", context)


class ImageUploadView(View):
    def get(self, request):
        form = ImageUploadForm()
        return render(request, "planner/image_upload.html", {"form": form})

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(
                "planner:image_list"
            )  # Перенаправление на страницу со списком изображений
        return render(request, "planner/image_upload.html", {"form": form})


class DeleteImageView(View):
    def get(self, request, image_id):
        image = get_object_or_404(Image, id=image_id)
        image.delete()
        return redirect("planner:image_list")


class AddToHomeView(View):
    def get(self, request, image_id):
        image = get_object_or_404(Image, id=image_id)
        post = get_object_or_404(Post, pk=12)  # Получаем пост с pk=12
        post.image = image  # Устанавливаем изображение
        post.save()  # Сохраняем изменения
        return JsonResponse(
            {"success": True, "message": "Изображение добавлено на главную!"}
        )


class LunchRegistrationView(View):
    template_name = "planner/registration_or_feedback.html"

    def get(self, request):
        # Логика вычисления даты
        # now = datetime.strptime("20.12.24 17:00:01", "%d.%m.%y %H:%M:%S")
        now = datetime.now()
        current_weekday = now.weekday()

        if current_weekday == 4 and now.time() > time(17, 0) or (current_weekday == 5):
            error_message = "Registration is over"
            return redirect(
                f"{reverse('planner:lunch_closed')}?message={error_message}"
            )

        form = LunchParticipantForm()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "title": "Registracija šeštadienio pietums",
                "register_lunch": True,
                "header_title": "Registracija šeštadienio pietums",
                "text": "Gerbiamieji Šri Šri Nitai Gaurasundaros Šventyklos svečiai! Tam, kad prasado užtektų visiems, prašome pranešti iš anksto, kiek porcijų pietų Jūs pageidaujate.",
            },
        )

    def post(self, request):
        form = LunchParticipantForm(request.POST)
        print("Мы в методе post")

        # Защита от спама роботов
        if form.is_valid():
            if form.cleaned_data.get("robot"):
                print("Это робот")
                return redirect("planner:lunch_success")
            if not form.cleaned_data.get("error_message"):
                participant = form.save()

                User = get_user_model()
                users = User.objects.values_list("email", flat=True)

                # Формируем текст уведомления
                subject = (
                    f"{participant.name} зарегистрировался на обед {participant.date}"
                )
                message = (
                    f"Пользователь по имени {participant.name} с email {participant.email},\n"
                    f"зарегистрировался на субботний обед, который состоится: {participant.date}.\n"
                    f"Количество порций: {participant.portions}"
                )
                if participant.comment:
                    message += f",\nКомментарий: {participant.comment}"

                # Создаем объект Task в базе данных
                Task.objects.create(subject=subject, message=message)

                # Отправляем уведомления зарегистрированным пользователям
                send_mail(subject, message, participant.email, users)

                # Отправляем уведомления в телеграм от имени бота
                base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

                for chat_id in TELEGRAM_CHAT_IDS:
                    payload = {"chat_id": chat_id, "text": message}
                    requests.post(base_url, data=payload)

                return redirect("planner:lunch_success")

        print("Форма не валидна")
        if form.cleaned_data.get("error_message"):
            error_message = form.cleaned_data.get("error_message")
            return redirect(
                f"{reverse('planner:lunch_closed')}?message={error_message}"
            )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "title": "Регистрация на обед",
                "errors": form.errors,  # Можно передать ошибки в контекст для отображения на странице
            },
        )


class LunchSuccessView(View):
    template_name = "planner/success.html"
    context = {
        "title": "Jūs esate užsiregistravę!",
        "form": "обед",
    }

    def get(self, request):
        return render(request, self.template_name, context=self.context)


class LunchClosedView(View):
    template_name = "planner/success.html"

    def get(self, request):
        message = request.GET.get("message")
        context = {
            "title": "Registracija nepavyko",
            "form": "Регистрация не удалась",
            "message": message,
        }
        return render(request, self.template_name, context=context)


class LunchParticipantListView(ListView):
    template_name = "planner/lunch_participants.html"

    def get(self, request):
        one_day_ago = timezone.now() - timedelta(days=1)
        participants = LunchParticipant.objects.filter(date__gte=one_day_ago)
        context = {
            "participants": participants,
        }

        return render(request, self.template_name, context)


class AllLunchParticipantListView(ListView):
    model = LunchParticipant
    template_name = "planner/lunch_participants.html"
    context_object_name = "participants"


class FeedbackView(View):
    template_name = "planner/registration_or_feedback.html"  # Универсальное название

    def get_context_data(self):
        return {"title": "Atsiliepimai", "header_title": "Atsiliepimai"}

    def get(self, request):
        context = self.get_context_data()
        form = FeedbackForm()
        context["form"] = form
        return render(request, self.template_name, context)

    def post(self, request):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("robot"):
                print("Это робот")
                return redirect("planner:feedback_success")

            feedback = form.save()

            subject = f"Обратная связь от {feedback.name}"
            message = f"Пользователь по имени {feedback.name} с email {feedback.email}, оставил обратную связь:\n{feedback.text}"
            # Создаем объект Task в базе данных
            Task.objects.create(subject=subject, message=message)

            User = get_user_model()
            users = User.objects.values_list("email", flat=True)

            # Отправляем уведомления зарегистрированным пользователям
            send_mail(subject, message, feedback.email, users)

            # Отправляем уведомления в телеграм от имени бота
            base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

            for chat_id in TELEGRAM_CHAT_IDS:
                payload = {"chat_id": chat_id, "text": message}
                requests.post(base_url, data=payload)

            return redirect(
                "planner:feedback_success"
            )  # Перенаправление на страницу успеха

        context = self.get_context_data()
        context["form"] = form
        return render(request, self.template_name, context)


class FeedbackSuccessView(View):
    template_name = "planner/success.html"
    context = {
        "title": "Žinutė išsiųsta!",
    }

    def get(self, request):
        return render(request, self.template_name, context=self.context)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(is_admin), name="dispatch")
class LunchParticipantDeleteView(DeleteView):
    model = LunchParticipant
    template_name = "planner/delete_person.html"
    success_url = reverse_lazy("planner:lunch_participants")
    extra_context = {"path": "planner:lunch_participants"}


class PageNotFoundView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "planner/404.html", {"path": request.path}, status=404)


from django.shortcuts import render
from django.views import View

from .forms import TextForm
from .models import Text


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(is_admin), name="dispatch")
class TextView(View):
    template_name = "planner/text.html"

    def get(self, request, *args, **kwargs):
        form = TextForm()
        return render(
            request,
            self.template_name,
            {"myform": form, "editor_open": True},
        )

    def post(self, request, *args, **kwargs):
        form = TextForm(request.POST)
        if form.is_valid():
            text = form.save()
            return redirect("planner:text_detail", pk=text.pk)
        return render(
            request,
            self.template_name,
            {"myform": form, "editor_open": True},
        )


class TextDetailView(DetailView):
    model = Text
    template_name = (
        "planner/text_detail.html"  # Укажи свой шаблон для отображения текста
    )
    context_object_name = "text"

    def get_object(self):
        # Получаем объект текста по pk
        return get_object_or_404(Text, pk=self.kwargs["pk"])


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(is_admin), name="dispatch")
class TextUpdateView(UpdateView):
    model = Text
    form_class = TextForm
    template_name = "planner/text.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["myform"] = context["form"]
        return context

    def get_success_url(self):
        return reverse_lazy("planner:text_detail", kwargs={"pk": self.object.pk})


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(is_admin), name="dispatch")
class DraftTextView(DetailView):
    template_name = "planner/post.html"
    extra_context = {"title": "Черновик"}

    def get_object(self, queryset=None):
        return Post.objects.get(pk=18)
