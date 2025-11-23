from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year = models.IntegerField()
    # The "Stub": user uploads a fake PDF here
    pdf_stub = models.FileField(upload_to='books/', blank=True, null=True)

    def __str__(self):
        return self.title

class Borrowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_overdue(self):
        # 10 Minute Limit Logic
        now = timezone.now()
        diff = now - self.borrowed_at
        return diff.total_seconds() > 600 # 600 seconds = 10 mins
    
    @property
    def remaining_time(self):
        now = timezone.now()
        diff = now - self.borrowed_at
        remaining = 600 - diff.total_seconds()
        return int(remaining / 60) if remaining > 0 else 0