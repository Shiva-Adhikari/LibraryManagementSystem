import time, os
from addbooks import AddBooksLibrary
from readbooks import ReadBooks
from issuebooks import IssueBooks
from returnbooks import ReturnBooks

while True:
    print('1. Add Book to Library')
    print('2. List of All Library Books')
    print('3. Issue Book From Library')
    print('4. Return Book to Library')
    print('0. Exit\n')

    choose = input("Select the List: ")
    print()

    try:
        select = int(choose)
        match select:
            case 1:
                os.system('clear')
                add_books = AddBooksLibrary()

                add_books.read_books()
                add_books.add_books()
                os.system('clear')

            case 2:
                os.system('clear')
                read_books = ReadBooks()
                read_books.read_books()
                input("\nPress Any Key...")
                os.system('clear')

            case 3:
                os.system('clear')
                read_books = ReadBooks()
                read_books.read_books()

                issue_books = IssueBooks()
                issue_books.issue_books()
                issue_books.user_read_books()
                issue_books.user_add_books()
                os.system('clear')

            case 4:
                os.system('clear')
                return_books = ReturnBooks()
                return_books.user_issued_books()

                return_books.return_books()
                return_books.user_read_books()
                return_books.user_add_books()
                os.system('clear')

            case 0:
                print("Thank You For your Time")
                exit()

            case _:
                print("Enter a Valid Input [ 1 to 4 ]")
                input("Press Any Key...")

    except ValueError:
        print("Please Enter a Number not String")
        input("Press Any Key...")
