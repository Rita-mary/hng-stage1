from django.db import models

# Create your models here.
class AnalyzedString(models.Model):
    id = models.CharField(primary_key=True, max_length=64)  
    value = models.TextField(unique=True)  
    length = models.PositiveIntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.PositiveIntegerField()
    word_count = models.PositiveIntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.value[:50]}..." 