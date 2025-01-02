from typing import List
import click
import json
import os
import logging


def _library_books():
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(root_path, 'data/')
    os.makedirs(data_dir, exist_ok=True)     # create dir if not exist
    library_books = os.path.join(data_dir, 'LibraryBooks.json')
    return library_books


library_books = _library_books()
categories = {}


def read_books(categories, library_books):
    """ read books from file """
    try:
        with open(library_books, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if isinstance(categories, dict):
            categories = data
        else:
            logging.warning('Warning: File not found. Creating new library.')
            click.echo('Warning: Invalid file format. Creating new library.')
            categories = {}
        return categories
    except (FileNotFoundError, json.JSONDecodeError) as e:
        click.echo(f'Error loading library: {str(e)}. Creating new library.')
        categories = {}
        return categories
    except click.Abort:
        click.echo('\nOperation Cancel')


@click.command()
@click.option(
    '--category',
    prompt=(
        'What Type of book you want to ADD in Library'
        ).lower(),
    type=str)
@click.option(
    '--num_books',
    prompt=(
        'How Many books you want to add in Library'
        ).lower(),
    type=click.IntRange(min=1),
    default=1)
def write_books(category, num_books):
    """ Write books in files """
    global categories
    # if list is empty then it create list
    if category not in categories:
        categories[category]: List = []
    for i in range(num_books):
        book_name = click.prompt(
            f'\nEnter "{category}" Book Name {i+1} '
            ).lower()
        author_name = click.prompt(f'Enter "{category}" Author name').lower()
        book_info = {
            'Id': len(categories[category]) + 1,
            'Title': book_name,
            'Author': author_name,
            'Available': 1
        }
        categories[category].append(book_info)    # append in dictionary
    try:
        with open(library_books, 'w', encoding='utf-8') as file:
            json.dump(categories, file, indent=4)
            click.echo('Data Successfully Saved in File\n')
    except Exception as e:
        logging.error(
            f'Failed to save in file(add_books): {str(e)}',
            exc_info=True)
        click.echo(f'failed to save in file: {str(e)}')
    input("Press Any Key...")


def main():
    """ Main entry point for the library management system."""
    global categories, library_books
    categories = read_books(categories, library_books)
    write_books()
