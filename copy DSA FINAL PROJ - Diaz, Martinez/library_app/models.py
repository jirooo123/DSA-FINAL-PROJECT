from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


BORROW_DURATION_HOURS = 24
BORROW_SECONDS = BORROW_DURATION_HOURS * 3600 

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year = models.IntegerField()
    pdf_stub = models.FileField(upload_to='books/', blank=True, null=True)
    
    quantity = models.IntegerField(default=3) 

    def __str__(self):
        return self.title


    @property
    def available_stock(self):
        active_borrows = self.borrowing_set.count()
        return self.quantity - active_borrows

class Borrowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_overdue(self):
        now = timezone.now()
        diff = now - self.borrowed_at
        return diff.total_seconds() > BORROW_SECONDS 
    
    @property
    def remaining_time(self):
        now = timezone.now()
        diff = now - self.borrowed_at
        remaining = BORROW_SECONDS - diff.total_seconds()
        
        return int(remaining / 60) if remaining > 0 else 0