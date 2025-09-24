from django.db import models

# Create your models here.
from django.db import models

class ChatLog(models.Model):
    """Almacena logs de interacciones del chatbot."""

    question = models.TextField()
    answer = models.TextField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)  # se guarda la hora automática

    def __str__(self):
        return f"[{self.created_at}] {self.question[:50]}..."
