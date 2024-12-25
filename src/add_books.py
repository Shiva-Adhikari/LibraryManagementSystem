import click
import json
from pathlib import Path
from typing import List, Dict


file_path = Path('data/LibraryBooks.json').resolve()
categories = {}

def read_books(categories, file_path):
    """ read books from file """
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            click.echo('File not found | Creating new library')
            data = {}
        # check if dictionary is present or not (like{'a': 'b'})
        if isinstance(categories, dict):
            categories = data
        else:
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
@click.option('--category', prompt=('What Type of book you want to ADD in Library: ').lower(), type=str)
@click.option('--num_books', prompt=('How Many books you want to add in Library: '), type=click.IntRange(min=1), default=1)
def write_books(category, num_books):
    """ Write books in files """
    global categories
    # if list is empty then it create list
    if category not in categories:
        categories[category]: List= []
    for i in range(num_books):
        book_name = click.prompt(f'Enter "{category}" Book Name {i+1}.: ').lower()
        author_name = click.prompt(f'Enter "{category}" Author name: ').lower()
        book_info = {
            'Id': len(categories[category]) + 1,
            'Title': book_name,
            'Author': author_name
        }
        categories[category].append(book_info)    #append in dictionary
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(categories, file, indent=4)
            click.echo('Data Successfully Saved in File\n')
    except Exception as e:
        click.echo(f'failed to save in file: {str(e)}')
    input("Press Any Key...")

def main():
    """ Main entry point for the library management system."""
    global categories, file_path
    categories = read_books(categories, file_path)
    write_books()

if __name__ == '__main__':
    main()
