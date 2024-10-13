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
    start_date = models.DateField(unique=True)
    end_date = models.DateField()
    image = models.ImageField(
        upload_to='weekly_images/', blank=True, null=True)


class DayEvents(models.Model):
    date = models.DateField()
    lecturer = models.ForeignKey(Lecturer, blank=True, null=True, on_delete=models.CASCADE)
    chef = models.ForeignKey(Chef, blank=True, null=True, on_delete=models.CASCADE)
    week_events = models.ForeignKey(
        WeekEvents, related_name='events', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - Lecturer: {self.lecturer}, Chef: {self.chef}"


class Post(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title
