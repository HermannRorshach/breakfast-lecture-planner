from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from planner.models import Post, LastScheduleUpdate 
from calendar_utils.utils import get_next_day_with_time


class Command(BaseCommand):
    help = "Переносит прошлую неделю из Post(pk=12) в Post(pk=17) один раз за неделю."

    SCHEDULE_DAY = 6  # воскресенье (0=понедельник, 6=воскресенье)
    SCHEDULE_TIME = (23, 50, 0)  # 23:50:00

    def handle(self, *args, **options):
        now = timezone.localtime(timezone.now())

        # Получаем ближайший прошлый понедельник (начала недели)
        today = now.date()
        weekday = today.weekday()
        
        # вычисляем следующее воскресенье 23:50
        context = {
            "target_day": self.SCHEDULE_DAY,
            "target_time": self.SCHEDULE_TIME,
            "current_weekday": weekday,
            "current_date": today,
            "now": now,
        }
        next_sunday_dt = get_next_day_with_time(context)
        last_sunday_dt = next_sunday_dt - timedelta(days=7)

        # Приводим к aware
        last_sunday_dt = timezone.make_aware(last_sunday_dt, timezone.get_current_timezone())
        next_sunday_dt = timezone.make_aware(next_sunday_dt, timezone.get_current_timezone())

        # Проверяем, была ли команда выполнена в текущем интервале
        last_update_obj = LastScheduleUpdate.objects.first()
        # print("last_update_obj.updated_at =", last_update_obj.updated_at, type(last_update_obj.updated_at),
        #       "last_sunday_dt =", last_sunday_dt, type(last_sunday_dt),
        #       "next_sunday_dt =", next_sunday_dt, type(next_sunday_dt))
        if last_update_obj and last_sunday_dt < last_update_obj.updated_at <= next_sunday_dt:
            self.stdout.write(self.style.NOTICE("Команда уже выполнена в текущем интервале."))
            return

        # Работаем с постами
        source_post = Post.objects.get(pk=12)
        target_post = Post.objects.get(pk=17)

        content = source_post.content
        start_idx = content.find("## savaitė")
        if start_idx == -1:
            self.stdout.write(self.style.ERROR("Не найдено начало блока ## savaitė"))
            return

        end_idx = content.find("## savaitė", start_idx + len("## savaitė"))
        if end_idx == -1:
            end_idx = len(content)

        extracted = content[start_idx:end_idx].strip()
        if not extracted:
            self.stdout.write(self.style.ERROR("Вырезанный блок пустой"))
            return

        # Обновляем в транзакции
        with transaction.atomic():
            # Вставляем в начало target_post
            target_post.content = f"{extracted}\n\n{target_post.content}"
            target_post.save(update_fields=["content"])

            # Убираем вырезанный блок из source_post
            source_post.content = content[:start_idx] + content[end_idx:]
            source_post.save(update_fields=["content"])

            # обновляем LastScheduleUpdate
            if last_update_obj:
                last_update_obj.updated_at = now
                last_update_obj.save(update_fields=["updated_at"])
            else:
                LastScheduleUpdate.objects.create(updated_at=now)


        self.stdout.write(self.style.SUCCESS("Расписание успешно обновлено"))
