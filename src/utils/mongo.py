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


# def _issue_books(
#         department_name, book_name):
#     is_exists = Books.objects(**{
#         f'{department_name}__Title': book_name,
#         f'{department_name}__Available__gt': 0
#     }).update_one(
#         inc={f'{department_name}.$.Available': -1}
#     )

#     if is_exists:
#         print('successfully issue books')
#     else:
#         print('not issue books')


# if __name__ == '__main__':
#     _issue_books('bca', 'x')

'''
**{
        # f'inc__{department_name}__S__Available': -1,
        # # f'push__{department_name}__S__UserDetails': {
        #     # 'Username': username,
        #     # 'Email': email,
        #     # 'Days': to_date,
        #     # 'IssueDate': issue_date,
        #     # 'DueWarning': due_warning,
        #     # 'DueDate': due_date,
        # # }
    }
'''


## raw string working...
# def issue_books(
#         department_name, book_name,
#         username, email, to_date, issue_date, due_warning, due_date):
#     is_exists = Books.objects(**{
#         f'{department_name}__Title': book_name,
#         f'{department_name}__Available__gt': 0
#     }).update_one(
#         __raw__={
#                 '$inc': {
#                     f'{department_name}.$.Available': -1
#                 },

#                 '$push': {
#                     f'{department_name}.$.UserDetails':
#                         {
#                             'Username': username,
#                             'Email': email,
#                             'Days': to_date,
#                             'IssueDate': issue_date,
#                             'DueWarning': due_warning,
#                             'DueDate': due_date,
#                         }

#                 }
#             }
#     )

#     if is_exists:
#         print('successfully issued book')
#     else:
#         print('could not issue book')


# if __name__ == '__main__':
#     issue_books('bca', 'a', 'usernme', 'meia@dfa.fd', 0, 0, 0, 0)


# def issue_books(
#         department_name, book_name,
#         username, email, to_date, issue_date, due_warning, due_date):
#     # Use $elemMatch to ensure both Title and Available conditions are met by the same element
#     is_exists = Books.objects(**{
#         f'{department_name}__elemMatch': {
#             'Title': book_name,
#             'Available__gt': 0
#         }
#     }).update_one(
#         __raw__={
#             '$inc': {
#                 f'{department_name}.$.Available': -1
#             },
#             '$push': {
#                 f'{department_name}.$.UserDetails': {
#                     'Username': username,
#                     'Email': email,
#                     'Days': to_date,
#                     'IssueDate': issue_date,
#                     'DueWarning': due_warning,
#                     'DueDate': due_date,
#                 }
#             }
#         }
#     )

#     if is_exists:
#         print('Successfully issued book')
#     else:
#         print('Could not issue book')


# if __name__ == '__main__':
#     issue_books('bca', 'c', 'usernme', 'meia@dfa.fd', 0, 0, 0, 0)


# for _ in range(5):


# working with raw query
# def issue_books(
#         department_name, book_name,
#         username, email, to_date, issue_date, due_warning, due_date):
#     # Construct a raw query to use $elemMatch explicitly
#     raw_query = {
#         department_name: {
#             '$elemMatch': {
#                 'Title': book_name,
#                 'Available': {'$gt': 0}
#             }
#         }
#     }

#     # Use the raw query to find the document
#     update_result = Books.objects(__raw__=raw_query).update_one(
#         __raw__={
#             '$inc': {
#                 f'{department_name}.$.Available': -1
#             },
#             '$push': {
#                 f'{department_name}.$.UserDetails': {
#                     'Username': username,
#                     'Email': email,
#                     'Days': to_date,
#                     'IssueDate': issue_date,
#                     'DueWarning': due_warning,
#                     'DueDate': due_date,
#                 }
#             }
#         }
#     )

#     if update_result:
#         print('Successfully issued book')
#     else:
#         print('Could not issue book')


# if __name__ == '__main__':
    # issue_books('bca', 'c', 'usernme', 'meia@dfa.fd', 0, 0, 0, 0)
