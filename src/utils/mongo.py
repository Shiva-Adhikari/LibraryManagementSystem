# third party modules
from src.models import Books
from src.utils import logger


def insert_books(department_name: str, new_books: list[int | str]):
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
        return books
    except Exception as e:
        logger.error(f'Failed to insert books {e}', exc_info=True)
        print(f'Failed to insert books...: {e}')
