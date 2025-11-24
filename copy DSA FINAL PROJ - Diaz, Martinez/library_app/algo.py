import operator

# --- 1. HASHING ---
def build_id_hash_map(books_list):
    book_map = {}
    for book in books_list:
        book_map[book.id] = book
    return book_map

# --- 2. MERGE SORT (Updated for Reversing) ---
def merge_sort(books, key='title', reverse=False):
    if len(books) <= 1:
        return books

    mid = len(books) // 2
    left = merge_sort(books[:mid], key, reverse)
    right = merge_sort(books[mid:], key, reverse)

    return merge(left, right, key, reverse)

def merge(left, right, key, reverse):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        val_left = getattr(left[i], key)
        val_right = getattr(right[j], key)
        
        if isinstance(val_left, str): val_left = val_left.lower()
        if isinstance(val_right, str): val_right = val_right.lower()

        # LOGIC FLIP: If reverse is True, we swap the comparison
        if reverse:
            condition = val_left > val_right # Descending (Z-A or 2025-2000)
        else:
            condition = val_left < val_right # Ascending (A-Z or 2000-2025)

        if condition:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
            
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# --- 3. BINARY SEARCH ---
def binary_search(sorted_books, target_title):
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

# --- 4. BINARY SEARCH TREE ---
class BSTNode:
    def __init__(self, book):
        self.book = book
        self.left = None
        self.right = None

def insert_bst(root, book):
    if root is None:
        return BSTNode(book)
    if book.year < root.book.year:
        root.left = insert_bst(root.left, book)
    else:
        root.right = insert_bst(root.right, book)
    return root

# Standard (Ascending): Left -> Root -> Right
def inorder_traversal(root, result_list):
    if root:
        inorder_traversal(root.left, result_list)
        result_list.append(root.book)
        inorder_traversal(root.right, result_list)

# NEW: Reverse (Descending): Right -> Root -> Left
def reverse_inorder_traversal(root, result_list):
    if root:
        reverse_inorder_traversal(root.right, result_list)
        result_list.append(root.book)
        reverse_inorder_traversal(root.left, result_list)