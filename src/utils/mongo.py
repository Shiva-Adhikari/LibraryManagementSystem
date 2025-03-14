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
        books = Books.objects(**{is_exists: True}).update_one(
            **{f'push_all__{department_name}': new_books},
            upsert=True
            )
        if books:
            return books
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
    is_exists = Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': book_name}
        }).update_one(
        **{f'pull__{department_name}': {'Title': book_name}}
        )
    if is_exists:
        return is_exists


def _find_books(department_name: str, book_name: str):
    """to search books

    Args:
        department_name (str): book category
        book_name (str): book name

    Returns:
        int: it return 1, mean successfully find book
    """
    is_exists = Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': book_name}
    })
    if is_exists:
        return is_exists


def _update_books(
        department_name: str, old_book_name: str, new_books: BookCategories):
    """to update books

    Args:
        department_name (str): book category
        old_book_name (str): previous book name
        new_books (_type_): BookCategory Model Instance

    Returns:
        int: 1 mean successfully updated book
    """
    is_exists = Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': old_book_name}
    }).update_one(
        __raw__={
            '$set': {
                f'{department_name}.$.Title': new_books.Title,
                f'{department_name}.$.Author': new_books.Author,
                f'{department_name}.$.Available': new_books.Available
            }
        }
    )
    if is_exists:
        return is_exists
