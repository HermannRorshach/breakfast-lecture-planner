from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from planner.models import DailySchedule, Post
from planner.services.schedule_parser import (
    parse_schedule,
    parse_week_number,
    replace_day_content,
)
from planner.services.schedule_archive import archive_previous_week


WEEKDAYS = [
    "Pirmadienis",
    "Antradienis",
    "Trečiadienis",
    "Ketvirtadienis",
    "Penktadienis",
    "Šeštadienis",
    "Sekmadienis",
]


def week_html(year, week, wrapped=False):
    heading = f'<h2 style="margin-left:0">SAVAITĖ № {week}</h2>'
    if wrapped:
        heading = f"<blockquote>{heading}</blockquote>"
    days = []
    for weekday, name in enumerate(WEEKDAYS, start=1):
        value = date.fromisocalendar(year, week, weekday)
        days.append(
            f'<h6 style="margin-left:0">{value.day} d. {name}</h6><p>day-{weekday}</p>'
        )
    return heading + "".join(days)


class ScheduleParserTests(TestCase):
    def test_accepts_tolerant_week_markers_without_regular_expression(self):
        for marker in ("savaitė—33", "SAVAITĖ - 33", "savaitė № 33", "savaite#33"):
            self.assertEqual(parse_week_number(marker), 33)

    def test_resolves_previous_year_week_before_week_one(self):
        content = week_html(2025, 52, wrapped=True) + week_html(2026, 1)
        parsed = parse_schedule(content, reference_date=date(2026, 1, 2))
        self.assertEqual(parsed.days[0].date, date(2025, 12, 22))
        self.assertEqual(parsed.days[-1].date, date(2026, 1, 4))

    def test_replaces_only_selected_day_body(self):
        content = week_html(2026, 1)
        changed = replace_day_content(
            content, date(2026, 1, 2), "<ul><li>Changed</li></ul>"
        )
        parsed = parse_schedule(changed, reference_date=date(2026, 1, 2))
        self.assertEqual(parsed.days[4].content, "<ul><li>Changed</li></ul>")
        self.assertEqual(parsed.days[3].content, "<p>day-4</p>")


class ScheduleEditingTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name="Админ")
        self.user = get_user_model().objects.create_user("admin", password="secret")
        self.user.groups.add(group)
        today = timezone.localdate()
        iso_year, iso_week, _ = today.isocalendar()
        self.content = week_html(iso_year, iso_week)
        Post.objects.create(pk=12, title="Schedule", content=self.content)
        Post.objects.create(pk=17, title="Archive", content="<p>Old archive</p>")
        self.first = Client()
        self.second = Client()
        self.first.force_login(self.user)
        self.second.force_login(self.user)

    def test_second_tab_cannot_acquire_lock(self):
        url = reverse("planner:schedule_edit_lock")
        self.assertEqual(
            self.first.post(url, {"action": "acquire", "token": "first"}).status_code,
            200,
        )
        self.assertEqual(
            self.second.post(url, {"action": "acquire", "token": "second"}).status_code,
            409,
        )
        self.first.post(url, {"action": "release", "token": "first"})
        self.assertEqual(
            self.second.post(url, {"action": "acquire", "token": "second"}).status_code,
            200,
        )

    def test_editor_gets_fresh_content_after_another_tab_saved(self):
        lock_url = reverse("planner:schedule_edit_lock")
        edit_url = reverse("planner:post-edit", args=[12])
        changed = self.content.replace("<p>day-1</p>", "<p>Fresh value</p>")
        self.first.post(lock_url, {"action": "acquire", "token": "first"})
        self.first.post(
            edit_url,
            {"content": changed, "edit_lock_token": "first"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.first.post(lock_url, {"action": "release", "token": "first"})
        self.second.post(lock_url, {"action": "acquire", "token": "second"})

        response = self.second.get(
            edit_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], changed)
        self.assertEqual(response.headers["Cache-Control"], "no-store, private")

        daily_response = self.second.get(
            reverse("planner:daily_schedule"),
            {"date": timezone.localdate().isoformat()},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(daily_response.headers["Cache-Control"], "no-store, private")

    def test_big_schedule_updates_daily_rows(self):
        lock_url = reverse("planner:schedule_edit_lock")
        self.first.post(lock_url, {"action": "acquire", "token": "first"})
        response = self.first.post(
            reverse("planner:post-edit", args=[12]),
            {"content": self.content, "edit_lock_token": "first"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DailySchedule.objects.count(), 7)

    def test_invalid_big_text_is_saved_without_changing_daily_rows(self):
        today = timezone.localdate()
        DailySchedule.objects.create(date=today, content="<p>Published</p>")
        lock_url = reverse("planner:schedule_edit_lock")
        self.first.post(lock_url, {"action": "acquire", "token": "first"})
        response = self.first.post(
            reverse("planner:post-edit", args=[12]),
            {"content": "<p>savanna — 33</p>", "edit_lock_token": "first"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["warning"])
        self.assertEqual(Post.objects.get(pk=12).content, "<p>savanna — 33</p>")
        self.assertEqual(
            DailySchedule.objects.get(date=today).content, "<p>Published</p>"
        )

    def test_daily_edit_updates_big_schedule(self):
        today = timezone.localdate()
        lock_url = reverse("planner:schedule_edit_lock")
        self.first.post(lock_url, {"action": "acquire", "token": "first"})
        response = self.first.post(
            reverse("planner:daily_schedule"),
            {
                "date": today.isoformat(),
                "daily-content": "<p>Updated in calendar</p>",
                "edit_lock_token": "first",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("Updated in calendar", Post.objects.get(pk=12).content)

    def test_archives_past_week_and_keeps_daily_history(self):
        today = timezone.localdate()
        current_monday = today - timedelta(days=today.weekday())
        previous_monday = current_monday - timedelta(days=7)
        previous_year, previous_week, _ = previous_monday.isocalendar()
        current_year, current_week, _ = current_monday.isocalendar()
        source = Post.objects.get(pk=12)
        source.content = week_html(previous_year, previous_week) + week_html(
            current_year, current_week
        )
        source.save(update_fields=["content"])
        DailySchedule.objects.create(date=previous_monday, content="<p>History</p>")

        self.assertEqual(archive_previous_week(reference_date=today), 1)
        self.assertNotIn(f"№ {previous_week}</h2>", Post.objects.get(pk=12).content)
        self.assertIn(f"№ {previous_week}</h2>", Post.objects.get(pk=17).content)
        self.assertTrue(DailySchedule.objects.filter(date=previous_monday).exists())
