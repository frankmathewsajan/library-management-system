from datetime import datetime
from .Database import Database
import bcrypt

Database.init()


class Accounts:
    def username() -> str:
        return Database.get(["username"],"users",f'auth = 1')[0][0] 
    def check_auth() -> bool:
        return Database.count('users','auth = 1') != 0

    def register(username: str, password: str, window) -> bool:
        if len(
            Database.get(
                ["username"],
                "users",
                f"username = '{username}'")) == 0:
            window['-MESSAGE-'].update(
                'Registration Success',text_color = 'green')
            password = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt())
            Database.insert('users', {
                'username': username,
                'password': password,
                'auth': True
            })
        else:
            window['-MESSAGE-'].update('User already exists')

    def login(username: str, password: str, window) -> bool:

        user_info = Database.get(["username","password"],"users",f"username = '{username}'")
        password = password.encode('utf-8')

        result = bcrypt.checkpw(password, user_info[0][1]) 
        if len(user_info) != 0 and result:
            window['-MESSAGE-'].update(
                'Login Success',text_color = 'green')
            Database.update('users', {
                'auth': True
            }, f"username = '{username}'")
        else:
            window['-MESSAGE-'].update(
                'User does not exist or incorrect password')
    def logout() -> bool:
        Database.update('users',{
                'auth' : 0
            })
    def reset_password():
        None


class Librarian(Accounts):
    def __init__(self, id, password, person):
        super().__init__(id, password, person)

    def add_book_item(self, book_item):
        None

    def block_member(self, member):
        None

    def un_block_member(self, member):
        None


class Member(Accounts):
    def __init__(self, id, password, person):
        super().__init__(id, password, person)
        self.__date_of_membership = datetime.date.today()
        self.__total_books_checkedout = 0

    def get_total_books_checkedout(self):
        return self.__total_books_checkedout

    def reserve_book_item(self, book_item):
        None

    def increment_total_books_checkedout(self):
        None

    def renew_book_item(self, book_item):
        None

    def checkout_book_item(self, book_item):
        pass

    def check_for_fine(self, book_item_barcode):
        pass

    def return_book_item(self, book_item):
        pass

    def renew_book_item(self, book_item):
        pass
