from django.contrib import admin
from .models import User, Mood, JournalEntry, CommunityPost, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Mood)
admin.site.register(JournalEntry)
admin.site.register(CommunityPost)
admin.site.register(Comment)