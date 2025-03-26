# third party modules
from src.models import Books, BookCategories
from src.utils import logger


def _insert_books(department_name: str, new_books: list[int | str]):
    """implemented mongoengine module to add books

    Args:
        department_name (str): category of book
        new_books (list[int | str]): list of books to add

    Returns:
        int: 1 indicate successfully saved in database
    """

    try:
        is_exists = f'{department_name}__exists'

        return Books.objects(**{is_exists: True}).update_one(
            **{f'push_all__{department_name}': new_books},
            upsert=True
            )

    except Exception as e:
        logger.error(f'Failed to insert books {e}', exc_info=True)
        print(f'Failed to insert books...: {e}')


def _delete_books(department_name: str, book_name: str):
    """delete books

    Args:
        department_name (str): category of book
        book_name (str): book name

    Returns:
        int: it return 1, mean successfully deleted book
    """
    return Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': book_name}
        }).update_one(
        **{f'pull__{department_name}': {'Title': book_name}}
        )


def _find_books(department_name: str, book_name: str):
    """to search books

    Args:
        department_name (str): book category
        book_name (str): book name

    Returns:
        int: it return 1, mean successfully find book
    """
    return Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': book_name}
    })


def _update_books(
        department_name: str, old_book_name: str, new_books: BookCategories):

    books = Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': old_book_name}
    }).first()

    if not books:
        return

    current_books = getattr(books, department_name, [])

    update_books = [
        {
            'Id': book.get('Id', new_books.Id),
            'Title': new_books.Title if book.get('Title', '').lower() == old_book_name.lower() else book['Title'],
            'Author': new_books.Author if book.get('Title', '').lower() == old_book_name.lower() else book['Author'],
            'Available': new_books.Available if book.get('Title', '').lower() == old_book_name.lower() else book['Available'],
        } for book in current_books
    ]

    setattr(books, department_name, update_books)

    try:
        books.save()
        return True
    except Exception:
        return
