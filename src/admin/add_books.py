# local modules
from src.models import Department, Books
from src.utils import _read_json, _send_response


@_send_response
@_read_json
def add_books(self, data):
    """Add book in database
    """

    if not data:
        return

    for category_name, book_list in data.items():
        # check if department exists
        department = Department.objects(name=category_name).first()

        if not department:
            # create new department
            department = Department(name=category_name, books=[])
            department.save()

        # now add each book and update the department
        for book_data in book_list:
            new_book = Books(
                title=book_data['title'].lower().strip(),
                author=book_data['author'].lower().strip(),
                available=book_data['available']
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
