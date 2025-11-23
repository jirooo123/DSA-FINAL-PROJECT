import operator

# --- 1. HASHING (For ID Search) ---
def build_id_hash_map(books_list):
    """
    Creates a Hash Map (Dictionary) for O(1) access by ID.
    """
    book_map = {}
    for book in books_list:
        book_map[book.id] = book
    return book_map

# --- 2. MERGE SORT (For Sorting Titles/Years) ---
def merge_sort(books, key='title'):
    """
    Sorts books list manually using Merge Sort algorithm.
    Complexity: O(n log n)
    """
    if len(books) <= 1:
        return books

    mid = len(books) // 2
    left = merge_sort(books[:mid], key)
    right = merge_sort(books[mid:], key)

    return merge(left, right, key)

def merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        # Get values dynamically (title or year)
        val_left = getattr(left[i], key)
        val_right = getattr(right[j], key)
        
        # Case insensitive for strings
        if isinstance(val_left, str): val_left = val_left.lower()
        if isinstance(val_right, str): val_right = val_right.lower()

        if val_left < val_right:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# --- 3. BINARY SEARCH (For Title Search) ---
def binary_search(sorted_books, target_title):
    """
    Searches for a book title. List MUST be sorted first.
    Complexity: O(log n)
    """
    low = 0
    high = len(sorted_books) - 1
    target_title = target_title.lower()

    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_books[mid].title.lower()

        if mid_val == target_title:
            return sorted_books[mid]
        elif mid_val < target_title:
            low = mid + 1
        else:
            high = mid - 1
    return None

# --- 4. BINARY SEARCH TREE (For Range Search) ---
class BSTNode:
    def __init__(self, book):
        self.book = book
        self.left = None
        self.right = None

def insert_bst(root, book):
    if root is None:
        return BSTNode(book)
    
    # Sort by Year for the Tree
    if book.year < root.book.year:
        root.left = insert_bst(root.left, book)
    else:
        root.right = insert_bst(root.right, book)
    return root

def search_range_bst(root, start_year, end_year, result_list):
    """
    Traverses tree to find books between start_year and end_year.
    """
    if root is None:
        return

    # If current node is greater than start, check left
    if root.book.year > start_year:
        search_range_bst(root.left, start_year, end_year, result_list)

    # If current node is within range, add to results
    if start_year <= root.book.year <= end_year:
        result_list.append(root.book)

    # If current node is less than end, check right
    if root.book.year < end_year:
        search_range_bst(root.right, start_year, end_year, result_list)