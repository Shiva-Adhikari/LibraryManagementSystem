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
        return books > 0
    except Exception as e:
        logger.error(f'Failed to insert books {e}', exc_info=True)
        print(f'Failed to insert books...: {e}')


def _delete_books(department_name: str, book_name: str):
    is_exists = Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': book_name}
        }).update_one(
        **{f'pull__{department_name}': {'Title': book_name}}
        )
    if is_exists:
        return is_exists


def _find_books(department_name: str, book_name: str):
    is_exists = Books.objects(**{
        f'{department_name}__exists': True,
        f'{department_name}__match': {'Title': book_name}
    })
    if is_exists:
        return is_exists


# if __name__ == '__main__':
    # _delete_books('bba', 'b')
    # _find_books('bbddds')
