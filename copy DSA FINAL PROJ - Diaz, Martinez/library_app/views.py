from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django import forms  # <--- NEW IMPORT
from .models import Book, Borrowing
# Make sure this matches your file name (either .utils or .algo)
from .algo import merge_sort, binary_search, build_id_hash_map, insert_bst, inorder_traversal, reverse_inorder_traversal

# --- 1. FORM FOR ADDING BOOKS ---
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'pdf_stub', 'quantity']

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
    all_books = list(Book.objects.all())
    
    query = request.GET.get('q')
    search_type = request.GET.get('type') 
    
    # SORT PARAMS
    sort_by = request.GET.get('sort') 
    direction = request.GET.get('dir', 'asc') # Default to ascending
    
    books_to_display = []
    message = ""

    # --- 1. SEARCH LOGIC ---
    if query:
        if search_type == 'id':
            try:
                target_id = int(query)
                book_map = build_id_hash_map(all_books)
                if target_id in book_map:
                    books_to_display = [book_map[target_id]]
                else:
                    message = "Book ID not found."
            except ValueError:
                message = "Invalid ID."
        elif search_type == 'title':
            sorted_books = merge_sort(all_books, key='title') # Default sort for binary search
            result = binary_search(sorted_books, query)
            if result:
                books_to_display = [result]
            else:
                books_to_display = [b for b in sorted_books if query.lower() in b.title.lower()]
                if not books_to_display:
                    message = "No exact match found."
                    books_to_display = sorted_books[:5]

    # --- 2. SORTING LOGIC ---
    else:
        if sort_by == 'year':
            # TREE SORT
            root = None
            for book in all_books:
                root = insert_bst(root, book)
            
            books_to_display = []
            
            if direction == 'desc':
                # Newest to Oldest (Right -> Root -> Left)
                reverse_inorder_traversal(root, books_to_display)
                message = "Sorted by Year: Newest First"
            else:
                # Oldest to Newest (Left -> Root -> Right)
                inorder_traversal(root, books_to_display)
                message = "Sorted by Year: Oldest First"

        elif sort_by == 'title':
            # MERGE SORT
            is_reverse = (direction == 'desc')
            books_to_display = merge_sort(all_books, key='title', reverse=is_reverse)
            
            if is_reverse:
                message = "Sorted Alphabetically: Z-A"
            else:
                message = "Sorted Alphabetically: A-Z"
        
        else:
            # Default fallback
            books_to_display = merge_sort(all_books, key='title')

    # --- CALCULATE NEXT LINKS ---
    # Logic: If I am currently 'title' and 'asc', clicking the link again should take me to 'title' and 'desc'
    next_title_dir = 'desc' if sort_by == 'title' and direction == 'asc' else 'asc'
    next_year_dir = 'asc' if sort_by == 'year' and direction == 'desc' else 'desc'

    return render(request, 'library_app/library.html', {
        'books': books_to_display, 
        'message': message,
        'current_sort': sort_by,       # To highlight active button
        'current_dir': direction,      # To show arrow
        'next_title_dir': next_title_dir, # For the link
        'next_year_dir': next_year_dir    # For the link
    })

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # STOCK CHECK LOGIC
    if book.available_stock > 0:
        Borrowing.objects.create(user=request.user, book=book)
    else:
        pass 
        
    return redirect('library_home')

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


@login_required
def return_book(request, borrowing_id):
    # Get the specific borrowing record for this user
    borrow_record = get_object_or_404(Borrowing, id=borrowing_id, user=request.user)
    
    # Delete it (Return the book)
    borrow_record.delete()
    
    return redirect('my_books')