from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_home, name='library_home'),
    path('signup/', views.signup, name='signup'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('my-books/', views.my_books, name='my_books'),
    path('add-book/', views.add_book, name='add_book'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('return-book/<int:borrowing_id>/', views.return_book, name='return_book'),
]