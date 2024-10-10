import os
from datetime import date, timedelta

from calendar_utils.utils import get_start_and_end_dates, get_weeks_in_year
from django.conf import settings
from django.db import models


class Lecturer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Chef(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class WeekEvents(models.Model):
    week_number = models.IntegerField()
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='weekly_images/', blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     if not self.pk:  # Определяем номера недели и даты только при создании
    #         last_week = WeekEvents.objects.order_by('-year', '-week_number').first()

    #         if last_week:
    #             num_weeks_in_year = get_weeks_in_year(last_week.year)

    #             if last_week.week_number < num_weeks_in_year:
    #                 self.week_number = last_week.week_number + 1
    #                 self.year = last_week.year
    #             else:
    #                 self.week_number = 1  # Начинаем с первой недели нового года
    #                 self.year = last_week.year + 1
    #         else:
    #             self.week_number = 1  # Если это первый объект, номер недели равен 1
    #             self.year = date.today().year

    #         # Определяем даты начала и конца недели
    #         self.start_date, self.end_date = get_start_and_end_dates(self.week_number, self.year)

    #         if not self.image:  # Устанавливаем изображение, если оно не загружено вручную
    #             image_path = f"weekly_images/{self.week_number}.jpg"
    #             full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)

    #             if os.path.exists(full_image_path):
    #                 self.image.name = image_path
    #             else:
    #                 self.image = None

    #     super().save(*args, **kwargs)


class DayEvents(models.Model):
    date = models.DateField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    chef = models.ForeignKey(Chef, on_delete=models.CASCADE)
    week_events = models.ForeignKey(WeekEvents, related_name='events', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - Lecturer: {self.lecturer}, Chef: {self.chef}"