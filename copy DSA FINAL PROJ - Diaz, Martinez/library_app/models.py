from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. DEFINE CONSTANTS (Easy to change later)
BORROW_DURATION_HOURS = 24
BORROW_SECONDS = BORROW_DURATION_HOURS * 3600  # 24 * 60 * 60 = 86400 seconds

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year = models.IntegerField()
    pdf_stub = models.FileField(upload_to='books/', blank=True, null=True)
    
    # NEW: Total Stock of the book
    quantity = models.IntegerField(default=3) 

    def __str__(self):
        return self.title

    # NEW: Calculate how many are left dynamically
    @property
    def available_stock(self):
        # Count how many people currently have this book borrowed
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
        # Use the constant we defined above
        return diff.total_seconds() > BORROW_SECONDS 
    
    @property
    def remaining_time(self):
        now = timezone.now()
        diff = now - self.borrowed_at
        remaining = BORROW_SECONDS - diff.total_seconds()
        
        # Return in Minutes (for display)
        return int(remaining / 60) if remaining > 0 else 0