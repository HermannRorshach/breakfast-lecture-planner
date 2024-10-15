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
