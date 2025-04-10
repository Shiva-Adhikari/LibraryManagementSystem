# built in module
import re

# local modules
from src.utils import _send_response, _read_get_query, route
from src.models import Books


@route('GET', '/api/admin/search-books')
@_send_response
@_read_get_query
def search_books(self, data):
    if not data:
        return
    book_name = data.get('book_name', '').strip()

    if not book_name:
        response = {
            'status': 'error',
            'message': 'missing book name'
        }
        return (response, 400)

    matching_books = Books.objects(title__regex=f"(?i).*{re.escape(book_name)}.*")
    if not matching_books:
        response = {
            'status': 'error',
            'message': 'no books found'
        }
        return (response, 404)

    '''
    # # using list comprehension
    # books_list = [{'title': book.title, 'author': book.author} for book in matching_books]
    '''

    # # without using list comprehension
    books_list = []
    for book in matching_books:
        books = {
            'title': book.title,
            'author': book.author
        }
        books_list.append(books)

    response = {
            'status': 'success',
            'message': books_list
        }
    return (response, 200)
