from django.db import transaction

from planner.models import DailySchedule, Post
from planner.services.schedule_parser import parse_schedule, replace_day_content


def sync_daily_schedules(post, reference_date=None):
    parsed = parse_schedule(post.content, reference_date=reference_date)
    with transaction.atomic():
        for day in parsed.days:
            DailySchedule.objects.update_or_create(
                date=day.date, defaults={"content": day.content}
            )
    return parsed


def sync_day_to_main_schedule(schedule_date, content):
    with transaction.atomic():
        post = Post.objects.select_for_update().get(pk=12)
        post.content = replace_day_content(post.content, schedule_date, content)
        post.save(update_fields=["content"])
        schedule, _ = DailySchedule.objects.update_or_create(
            date=schedule_date, defaults={"content": content}
        )
    return schedule, post
