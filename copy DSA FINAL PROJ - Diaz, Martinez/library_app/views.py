from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django import forms  # <--- NEW IMPORT
from .models import Book, Borrowing
# Make sure this matches your file name (either .utils or .algo)
from .algo import merge_sort, binary_search, build_id_hash_map, insert_bst, search_range_bst

# --- 1. FORM FOR ADDING BOOKS ---
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'pdf_stub']

# --- 2. ADMIN CHECK ---
def is_admin(user):
    return user.is_staff or user.is_superuser

# --- 3. VIEWS ---

def index_redirect(request):
    """
    Redirects root URL '' to either Library or Signup
    """
    if request.user.is_authenticated:
        return redirect('library_home')
    return redirect('signup')

def signup(request):
    if request.user.is_authenticated:
        return redirect('library_home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('library_home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def library_home(request):
    # Fetch ALL data (Convert to list to use Python DSA)
    all_books = list(Book.objects.all())
    
    query = request.GET.get('q')
    search_type = request.GET.get('type') # 'title', 'id', 'range'
    
    books_to_display = []
    message = ""

    # --- DEFAULT: DISPLAY ALL SORTED ALPHABETICALLY ---
    if not query:
        books_to_display = merge_sort(all_books, key='title')

    # --- SEARCH LOGIC ---
    else:
        if search_type == 'id':
            try:
                target_id = int(query)
                book_map = build_id_hash_map(all_books)
                if target_id in book_map:
                    books_to_display = [book_map[target_id]]
                else:
                    message = "Book ID not found."
            except ValueError:
                message = "Please enter a valid number for ID."

        elif search_type == 'title':
            sorted_books = merge_sort(all_books, key='title')
            result = binary_search(sorted_books, query)
            
            if result:
                books_to_display = [result]
            else:
                # Suggestion / Partial match
                books_to_display = [b for b in sorted_books if query.lower() in b.title.lower()]
                if not books_to_display:
                    message = "No exact match found. Try these?"
                    books_to_display = sorted_books[:5]

        elif search_type == 'range':
            try:
                start, end = map(int, query.split('-'))
                root = None
                for book in all_books:
                    root = insert_bst(root, book)
                
                found = []
                search_range_bst(root, start, end, found)
                books_to_display = found
                if not found:
                    message = f"No books found between {start} and {end}."
            except ValueError:
                message = "Format must be YYYY-YYYY (e.g. 2000-2010)"

    return render(request, 'library_app/library.html', {
        'books': books_to_display, 
        'message': message
    })

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Borrowing.objects.create(user=request.user, book=book)
    return redirect('my_books')

@login_required
def my_books(request):
    borrowed = Borrowing.objects.filter(user=request.user)
    return render(request, 'library_app/my_books.html', {'borrowed': borrowed})

# --- 4. NEW ADD BOOK VIEW (ADMIN ONLY) ---
@login_required
@user_passes_test(is_admin)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('library_home')
    else:
        form = BookForm()
    return render(request, 'library_app/add_book.html', {'form': form})



# --- ADD THIS TO THE BOTTOM OF views.py ---

@login_required
@user_passes_test(is_admin)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return redirect('library_home')