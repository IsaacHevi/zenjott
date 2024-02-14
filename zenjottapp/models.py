from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here
class User(AbstractUser):
    pass

class Mood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    MOODS = {
        "happy": "happy",
        "sad": "sad",
        "excited": "excited",
        "angry": "angry",
        "calm": "calm",
    }
    mood = models.CharField(max_length=10, choices=MOODS, default='happy')
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.timestamp} Mood"

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    short_content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    time = models.TimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)    

    def save(self, *args, **kwargs):
        if not self.short_content:
            self.short_content = self.content[:200]
        if not self.time:
            self.time = self.timestamp.time()
        if not self.date:
            self.date = self.timestamp.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s journal entry."

class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.time:
            self.time = self.timestamp.time()
        if not self.date:
            self.date = self.timestamp.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Post by {self.user.username}: {self.content}'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE)
    content = models.TextField(default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.time:
            self.time = self.timestamp.time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s comment on {self.post.content}"