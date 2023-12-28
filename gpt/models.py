from django.db import models
from django.contrib.auth import get_user_model

class Chat(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email+str(self.created_at)
