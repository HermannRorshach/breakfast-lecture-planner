from django.db import models


class Task(models.Model):
    subject = models.CharField(max_length=255)  # Тема письма
    message = models.TextField()  # Текст письма
    done = models.BooleanField(default=False)  # Выполнена ли задача

    def __str__(self):
        return f"Task {self.id} - {self.subject}"
