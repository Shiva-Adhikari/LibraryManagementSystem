# local modules
from src.models import Department, Books
from src.utils import _read_json, _send_response, route


@route('POST', r'^/api/admin/add-books/(?P<category>[^/]+)$')
@_send_response
@_read_json
def add_books(self, data):
    """Add book in database
    """

    if not data:
        return

    category_name = self.Category

    # check if department exists
    department = Department.objects(name=category_name).first()

    if not department:
        # create new department
        department = Department(name=category_name, books=[])
        department.save()

    # now add each book and update the department
    for book_details in data:
        new_book = Books(
            title=book_details['title'].lower().strip(),
            author=book_details['author'].lower().strip(),
            available=book_details['available']
        ).save()

        # add this book in the department's books list
        department.books.append(new_book)

    # save the department with all new books
    department.save()
    response = {
        'status': 'success',
        'message': 'Added Books Successfully'
    }
    return (response, 201)
