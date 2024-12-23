import json

class ReturnBooks:
    def __init__(self):
        self.user_book_category = {}
        self.user_book_name = ''
        self.user_book_author = ''
        self.books_type = ''
        self.books = ''


    def user_issued_books(self):
        try:
            with open('user_issue_books.json') as file:
                books = json.load(file)

                for books_category, books_lists in books.items():
                    print(f'{books_category}:'.capitalize())
                    # it print ------------------ this

                    for _ in range(50):
                        print('-',end='')
                    print()
                    print('Books Name:\t\tAuthor Name: ')

                    for book in books_lists:
                        print(book['Title'] + '\t\t\t' + book['Author'])
                    print()

        except FileNotFoundError:
            print("No books file found.")
        except json.JSONDecodeError:
            print("Your List is Empty.")
            input("Press Any key")
            return
            # print("Error reading the JSON file. File might be corrupted.")


    def return_books(self):
        books_types = input("What type of Books want to Return: ")
        self.books_type = books_types.lower()   # convert in lower case

        with open('user_issue_books.json', 'r') as file_read:
            self.books = json.load(file_read)

            # check if keys is empty or not if empty remove extra lists from file
            for books_category, books_list in self.books.items():
                if not books_list:
                    print('list is empty')
                    del self.books[books_category]
                    with open('user_issue_books.json', 'w') as file:
                        json.dump(self.books, file, indent=4)
                    return

            for books_category, books_list in self.books.items():

                if books_category == self.books_type:
                    input_book_name = input("Enter Book Name: ")
                    input_book_name = input_book_name.lower()

                    for book in books_list:
                        if book['Title'] == input_book_name:
                            self.user_book_name = book['Title']
                            self.user_book_author = book['Author']
                            books_list.remove(book)

        with open('user_issue_books.json', 'w') as file_write:
            json.dump(self.books, file_write, indent=4)


    def user_read_books(self):
        try:
            with open('books.json', 'r') as file_r:
                self.user_book_category = json.load(file_r)
                if isinstance(self.user_book_category, dict):
                    pass
                    # print('file is present')
                else:
                    print('file is not present')
                    self.user_book_category = {}
        except (FileNotFoundError, json.JSONDecodeError):
            print('creating file ...')
            self.user_book_category = {}


    def user_add_books(self):

        book_names = self.books_type
        if book_names not in self.user_book_category:
            self.user_book_category[book_names] = []

        book_info = {
            'Title' : self.user_book_name,
            'Author' : self.user_book_author
        }
        self.user_book_category[book_names].append(book_info)

        with open('books.json', 'w') as file_w:
            json.dump(self.user_book_category, file_w, indent=4)
            # print('done')

        input("\nPress Any Key...")
