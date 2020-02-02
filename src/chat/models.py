from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Message(models.Model):
    author      = models.ForeignKey(User, related_name="author_messages", on_delete=models.CASCADE)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author.username

    # since we should never load all the messages, load the most recent 30 first
    def last_10_messages(self):
        return Message.objects.order_by('-created_at').all()[:10]