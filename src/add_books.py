import click
import json
from pathlib import Path
from typing import List, Dict


class AddBooks:
    def __init__(self,file_path: str = '../data/LibraryBooks.json'):
        self.id = 0
        self.file_path = Path(file_path)
        self.categories: Dict[str, List[Dict]] = {}
        # self.data = {}

    def add(self) -> None:
        data = {}
        """ read books from file """
        try:
            if self.file_path.exists():
                with self.file_path.open('r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                click.echo('Unable to read file | File not exist')
            # check if dictionary is present or not {'a': 'b'}
            if isinstance(self.categories, dict):
                self.categories = data
            else:
                click.echo('Warning: Invalid file format. Creating new library.')
                self.categories = {}

        except (FileNotFoundError, json.JSONDecodeError) as e:
            click.echo(f'Error loading library: {str(e)}. Creating new library.')
            self.categories = {}
        except click.Abort:
            click.echo('\nOperation Cancel')

        """ Write books in files """
        category = click.prompt('What Type of book you want to ADD in Library: ', type=str).lower()
        num_books = click.prompt('How Many books you want to add in Library: ', type=click.IntRange(min=1), default=1)
        # if list is empty then it create list
        if category not in self.categories:
            self.categories[category] = []
        for i in range(num_books):
            book_name = click.prompt(f'Enter "{category}" Book Name {i+1}.: ').lower()
            author_name = click.prompt(f'Enter "{category}" Author name: ').lower()
            book_info = {
                'Id': len(self.categories[category]) + 1,
                'Title': book_name,
                'Author': author_name
            }
            self.categories[category].append(book_info)    #append in dictionary
        if self.file_path.exists():
            with self.file_path.open('w', encoding='utf-8') as file:
                json.dump(self.categories, file, indent=4)
                print('Data Successfully Saved in File')
        else:
            click.echo('Unable to read file | File not exist | Data Not Saved')

        # at last hold the screen
        input("\nPress Any Key...")

def main():
    """ Main entry point for the library management system."""
    add_books = AddBooks()
    add_books.add()

if __name__ == '__main__':
    main()
