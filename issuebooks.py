import json

class IssueBooks:
    def __init__(self):
        self.user_book_category = {}
        self.user_book_name = ''
        self.user_book_author = ''
        self.books_type = ''
        self.books = ''


    def issue_books(self):
        books_types = input("What type of Books you need: ")
        self.books_type = books_types.lower()

        # working in files to read data
        with open('books.json', 'r') as file_read:
            self.books = json.load(file_read)

            # seperate keys and values
            for books_category, books_list in self.books.items():

                # if books not found it exit program but save empty string in (file) as dictionary
                if self.books_type != books_category:
                    print("Book not available")
                    return

                if books_category == self.books_type:
                    input_book_names = input("Enter Book Name: ")
                    input_book_name = input_book_names.lower()

                    for book in books_list:
                        # match user input and dictionary keys
                        if book['Title'] == input_book_name:
                            self.user_book_name = book['Title']
                            self.user_book_author = book['Author']
                            books_list.remove(book)

        with open('books.json', 'w') as file_write:
            json.dump(self.books, file_write, indent=4)     # indent mean tab (four line)


    def user_read_books(self):
        try:
            with open('user_issue_books.json', 'r') as file_r:
                self.user_book_category = json.load(file_r)

                # check if dictionary is present in file
                if isinstance(self.user_book_category, dict):
                    pass
                    # print('file is present')
                else:
                    print('file is not present')
                    self.user_book_category = {}    # create new nested dictionary
        except (FileNotFoundError, json.JSONDecodeError):
            print('creating file ...')
            self.user_book_category = {}    # create new nested dictionary


    def user_add_books(self):

        book_names = self.books_type
        # If the book category is not already in the dictionary, create a new key-value pair
        if book_names not in self.user_book_category:
            self.user_book_category[book_names] = []

        book_info = {
            'Title' : self.user_book_name,
            'Author' : self.user_book_author
        }
        self.user_book_category[book_names].append(book_info)

        with open('user_issue_books.json', 'w') as file_w:
            json.dump(self.user_book_category, file_w, indent=4)

        # at last hold the screen
        input("\nPress Any Key...")


if __name__ == '__main__':
    issue_books = IssueBooks()
    issue_books.issue_books()
    issue_books.user_read_books()
    issue_books.user_add_books()