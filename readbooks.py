import json

class ReadBooks:
    def __init__(self):
        pass

    def read_books(self):
        try:
            with open('books.json') as file:
                books = json.load(file)
                for books_category, books_lists in books.items():
                    # if not books_lists: 
                            # books_lists.remove(books)
                            # del books[books_lists]
                            # with open('books.json', 'w') as file_rw:
                                # json.dump(books, file_rw, indent=4)
                    print(f'{books_category}:'.capitalize())
                    for _ in range(50):
                        print('-',end='')
                    print()
                    
                    print('Books Name:\t\tAuthor Name: ')

                    for book in books_lists:
                        # if not book:
                            # print('empty')
                        # if not book['Title']:
                        #     print('e')
                        #     books_lists.remove(book)
                        #     with open('books.json', 'w') as file_rw:
                        #         json.dump(books, file_rw, indent=4)
                        # print('a')
                        print(book['Title'].capitalize() + '\t\t\t' + book['Author'].capitalize())
                    print()

            


        except FileNotFoundError:
            print("Books Not Found.")
        except json.JSONDecodeError:
            print("Json File Can't be Read.")




if __name__ == '__main__':
    read_books = ReadBooks()
    read_books.read_books()
