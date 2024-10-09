from django.db import models

class Lecturer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Chef(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DayEvents(models.Model):
    date = models.DateField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    chef = models.ForeignKey(Chef, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} - Lecturer: {self.lecturer}, Chef: {self.chef}"
