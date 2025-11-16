from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Book, BorrowRecord
from .forms import BookForm, SignupForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def index(request):
    # default listing (ordered by title)
    books = Book.objects.all().order_by('title')
    return render(request, 'library_app/index.html', {'books': books})

def search(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'title')  # 'id' or 'title'
    results = []
    if query:
        if search_type == 'id':
            # hash-like lookup
            try:
                results = [Book.objects.get(book_id=query)]
            except Book.DoesNotExist:
                results = []
        else:
            # title/author search (case-insensitive contains)
            results = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            ).order_by('title')
    return render(request, 'library_app/search.html', {'results': results, 'query': query})

def book_detail(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    return render(request, 'library_app/book_detail.html', {'book': book})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            if Book.objects.filter(book_id=book_id).exists():
                messages.error(request, 'Book with this ID already exists.')
            else:
                form.save()
                messages.success(request, 'Book added.')
                return redirect('index')
    else:
        form = BookForm()
    return render(request, 'library_app/add_book.html', {'form': form})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    book.delete()
    messages.success(request, 'Book deleted.')
    return redirect('index')

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    BorrowRecord.objects.create(user=request.user, book=book)
    messages.success(request, 'Book borrowed. (record created)')
    return redirect('book_detail', book_id=book.book_id)

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created. Please log in.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'library_app/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'library_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')