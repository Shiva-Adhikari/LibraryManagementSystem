# local modules
from src.models import Department, Books
from src.utils import _read_json, _send_response


def add_books(handler):
    """Add book in database

    Args:
        handler: The request handler containing the JSON data
    """

    data = _read_json(handler)

    for category_name, book_list in data.items():
        # check if department exists
        existing_department = Department.objects(name=category_name).first()

        if existing_department:
            # if exists just add book to it
            department = existing_department
        else:
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
        return _send_response(handler, response, 200)
