import json

class AddBooksLibrary:
    def __init__(self):
        self.book_category = {}

    def read_books(self):
        try:
            # working with file
            with open('books.json', 'r') as file_r:
                self.book_category = json.load(file_r)

                # check if dictionary is present or not {'a': 'b'}
                if isinstance(self.book_category, dict):
                    pass
                    # print('file is present')
                else:
                    print('file is not present')
                    # if not this will create dictionary
                    self.book_category = {}

        except (FileNotFoundError, json.JSONDecodeError):
            # if file not found or error to decode it will replace whole dictionary
            # print('creating file ...')
            self.book_category = {}

    def add_books(self):
        book_names = input('What type of book you want to ADD in Library: ')
        book_names = book_names.lower()     # lower case

        # when user enter string value then it throw error and in loop it ask to enter number
        while True:
            try:
                number_books = int(input("How many books you want: "))
                break  # Exit the loop if the input is a valid integer
            except ValueError:
                print("Invalid input! Please enter a valid number, not a string.")

        # if list is empty then it create list
        if book_names not in self.book_category:
            self.book_category[book_names] = []
        
        for i in range(number_books):
            # user input
            book_name = input(f'Enter "{book_names}" Book Name {i+1}.: ')
            author_name = input(f'Enter "{book_name}" Author name: ')
            book_info = {
                'Title' : book_name,
                'Author' : author_name
            }
            self.book_category[book_names].append(book_info)    #append in dictionary

            # save in file as dict
            with open('books.json', 'w') as file_w:
                json.dump(self.book_category, file_w, indent=4)
                print('Successfully Saved')

        # at last hold the screen
        input("\nPress Any Key...")
