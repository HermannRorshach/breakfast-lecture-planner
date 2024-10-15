from django.db import models



class Post(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200)
    content = models.TextField()
    image = models.ForeignKey('Image', null=True, blank=True, on_delete=models.SET_NULL)  # Поле для хранения изображения

    def __str__(self):
        return self.title


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image uploaded at {self.uploaded_at}"


from django.db import models

class LunchParticipant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    portions = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 16)], default=1)
    comment = models.TextField(blank=True, null=True)
    date = models.DateField()  # Поле для даты обеда

    def __str__(self):
        return self.name
