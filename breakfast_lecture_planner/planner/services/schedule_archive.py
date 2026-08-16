from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from planner.models import LastScheduleUpdate, Post
from planner.services.schedule_parser import ScheduleStructureError, parse_schedule
from planner.services.schedule_sync import sync_daily_schedules


def archive_previous_week(reference_date=None):
    today = reference_date or timezone.localdate()
    current_monday = today - timedelta(days=today.weekday())
    with transaction.atomic():
        locked_source = Post.objects.select_for_update().get(pk=12)
        archive = Post.objects.select_for_update().get(pk=17)
        parsed = parse_schedule(locked_source.content, reference_date=today)
        if not any(monday == current_monday for monday, _ in parsed.week_blocks):
            raise ScheduleStructureError(
                [
                    f"Не найдено расписание текущей недели, начинающейся {current_monday:%d.%m.%Y}."
                ]
            )
        expired_blocks = [
            block for monday, block in parsed.week_blocks if monday < current_monday
        ]
        if not expired_blocks:
            return 0
        archive_html = "".join(str(node) for block in expired_blocks for node in block)
        for block in expired_blocks:
            for node in block:
                node.extract()
        locked_source.content = str(parsed.soup).strip()
        archive.content = f"{archive_html}{archive.content}"
        locked_source.save(update_fields=["content"])
        archive.save(update_fields=["content"])
        LastScheduleUpdate.objects.update_or_create(
            pk=LastScheduleUpdate.objects.values_list("pk", flat=True).first() or 1,
            defaults={"updated_at": timezone.now()},
        )
        sync_daily_schedules(locked_source, reference_date=today)
    return len(expired_blocks)
