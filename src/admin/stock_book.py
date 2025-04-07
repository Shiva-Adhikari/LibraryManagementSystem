# local modules
from src.utils import _send_response
from src.models import Books, Department


@_send_response
def stock_book(self):
    """Search for books with less than 5 available copies
    and find their department."""

    low_stock_book = Books.objects(available__lt=5)

    if not low_stock_book:
        response = {
            'status': 'success',
            'message': 'books not found with low stock'
        }
        return (response, 404)

    books_list = []
    for book in low_stock_book:
        book_info = {
            'title': book.title.capitalize(),
            'author': book.author.capitalize(),
            'available': book.available
        }

        department = Department.objects(books=book.id).first()
        if department:
            book_info['Department'] = department.name.capitalize()
        else:
            book_info['Department'] = 'Unknown'

        books_list.append(book_info)

    response = {
        'status': 'success',
        'message': books_list
    }
    return (response, 200)
