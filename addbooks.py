import json

class AddBooksLibrary:
    def __init__(self):
        self.book_category = {}

    def read_books(self):
        try:
            with open('books.json', 'r') as file_r:
                self.book_category = json.load(file_r)
                if isinstance(self.book_category, dict):
                    pass
                    # print('file is present')
                else:
                    print('file is not present')
                    self.book_category = {}

        except (FileNotFoundError, json.JSONDecodeError):
            print('creating file ...')
            self.book_category = {}

    def add_books(self):
        book_names = input('What type of book you want to ADD in Library: ')
        book_names = book_names.lower()
        while True:
            try:
                number_books = int(input("How many books you want: "))
                break  # Exit the loop if the input is a valid integer
            except ValueError:
                print("Invalid input! Please enter a valid number, not a string.")

        if book_names not in self.book_category:
            self.book_category[book_names] = []
        
        for i in range(number_books):
            book_name = input(f'Enter "{book_names}" Book Name {i+1}.: ')
            author_name = input(f'Enter "{book_name}" Author name: ')
            book_info = {
                'Title' : book_name,
                'Author' : author_name
            }
            self.book_category[book_names].append(book_info)
            with open('books.json', 'w') as file_w:
                json.dump(self.book_category, file_w, indent=4)
                print('Successfully Saved')

        input("\nPress Any Key...")




if __name__ == '__main__':
    add_books = AddBooksLibrary()
    add_books.read_books()
    add_books.add_books()