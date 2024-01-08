import os
import sys
import PySimpleGUI as sg
import bcrypt
import re

from classes.Constants import CHECKOUT_LIMIT, PASSWORD_REGEX, USERNAME_REGEX

from .Database import Database as DB

DB.init()


class Accounts:
    def username() -> str:
        return DB.get(["username"], "users", f"auth = 1")[0][0]

    def searches() -> list:
        username = Accounts.username()
        tuple_list = DB.get(
            ["username", "search"], "searches", f"username = '{username}'"
        )
        return list(map(lambda tup: tup[1], tuple_list)) if tuple_list else []

    def check_auth() -> bool:
        return DB.count("users", "auth = 1") != 0

    def register(username: str, password: str, window) -> bool:
        message = "User already exists"
        valid = True
        if not re.match(USERNAME_REGEX, username) or not re.match(
            PASSWORD_REGEX, password
        ):
            message = (
                "Invalid username"
                if not re.match(USERNAME_REGEX, username)
                else "Invalid password"
            )
            valid = False
        if (
            len(DB.get(["username"], "users", f"username = '{username}'")) == 0
            and valid
        ):
            window["-MESSAGE-"].update("Registration Success", text_color="green")

            password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            DB.insert(
                "users", {"username": username, "password": password, "auth": True}
            )
            sg.popup("Registration Success")
            return True
        else:
            window["-MESSAGE-"].update(message, text_color="red")
            return False

    def login(username: str, password: str, window) -> bool:

        user_info = DB.get(
            ["username", "password"], "users", f"username = '{username}'"
        )
        password = password.encode("utf-8")
        result = bcrypt.checkpw(password, user_info[0][1])
        if len(user_info) != 0 and result:
            window["-MESSAGE-"].update("Login Success", text_color="green")
            DB.update("users", {"auth": True}, f"username = '{username}'")
            sg.popup("Login Success")
            return True
        else:
            window["-MESSAGE-"].update("User does not exist or incorrect password")
            return False

    def logout():
        DB.update("users", {"auth": 0})
        sys.exit()

    def delete():
        DB.delete("users", f"username = '{Accounts.username()}'")
        sys.exit()

    def reset_password():
        ...

    def borrowed(columns: list) -> list:
        [f"a.{col}" for col in columns]
        return list(
            map(
                lambda e: e[0],
                DB.join_and_get(
                    [f"a.{col}" for col in columns],
                    "library",
                    "books",
                    f"a.uid = b.uid",
                    [f"b.username = '{Accounts.username()}'", "b.type = 'BORROWED'"],
                ),
            )
        )

    def purchased(columns: list) -> list:
        [f"a.{col}" for col in columns]
        return list(
            map(
                lambda e: e[0],
                DB.join_and_get(
                    [f"a.{col}" for col in columns],
                    "library",
                    "books",
                    f"a.uid = b.uid",
                    [f"b.username = '{Accounts.username()}'", "b.type = 'PURCHASED'"],
                ),
            )
        )

    def checkout_book(uid):
        borrowed = Accounts.borrowed(["uid"])
        username = Accounts.username()
        if uid and len(borrowed) < CHECKOUT_LIMIT and uid not in borrowed:
            DB.insert("books", {"uid": uid, "type": "BORROWED", "username": username})

            count = (
                int(DB.get(["checked_out"], "users", f"username = '{username}'")[0][0])
                + 1
            )
            DB.update("users", {"checked_out": count}, f"username = '{username}'")
            title, msg = "Success ✓✓✓", f"Added to Check Out List ✓, {count}/3"
        elif uid in borrowed:
            title, msg = "Error ×××", "Already in List ×"
        elif uid is None:
            title, msg = "Error ×××", "Please select a book from side bar ×"
        else:
            title, msg = "Error ×××", "List Already Full ×"

        from classes.Library import Library

        name = Library.books(["title"], "uid", uid)[0][0]
        sg.Popup(f"Name : {name}\n\n{msg}", title=title, keep_on_top=True)

    def add_money(amount: int) -> int:
        print(1)
        username = Accounts.username()
        balance = DB.get(["balance"], "users", f"username = '{username}'")[0][0]
        if isinstance(amount, int) and 1 <= amount <= 1000:
            DB.update(
                "users", {"balance": balance + amount}, f"username = '{username}'"
            )
            balance += amount
            sg.popup_ok(
                f"° Amount ₹{amount} credited ✓\nCurrent Balance = ₹{balance}",
                title="Transaction Message",
            )
        else:
            sg.popup_ok(
                f"° Amount must be between  ₹1 - ₹1000\nCurrent Balance = ₹{balance}",
                title="Failed Transaction Message",
            )
        return balance

    def purchase_book(uid):
        from classes.Library import Library

        purchased = Accounts.purchased(["uid"])
        username = Accounts.username()
        if uid and uid not in purchased:
            db_info = DB.get(
                ["purchased", "balance"], "users", f"username = '{username}'"
            )
            price = Library.books(["price"], "uid", uid)[0][0]
            count = int(db_info[0][0]) + 1
            balance = int(db_info[0][1])
            if price > balance:
                title, msg = "Failed", f"Insufficent Balance ✓, {count}"
            else:
                DB.insert(
                    "books", {"uid": uid, "type": "PURCHASED", "username": username}
                )
                DB.update(
                    "users",
                    {"purchased": count, "balance": int(balance - price)},
                    f"username = '{username}'",
                )
                title, msg = (
                    "Success ✓✓✓",
                    f"Purchase Done ✓, ₹{int(balance- price)}\- left",
                )
        elif uid in purchased:
            title, msg = "Error ×××", "Already Purchased ×"
        elif uid is None:
            title, msg = "Error ×××", "Please select a book from side bar ×"
        name = Library.books(["title"], "uid", uid)[0][0]
        sg.Popup(f"Name : {name}\n\n{msg}", title=title, keep_on_top=True)

    def return_book(book_item):
        pass

    def Refresh() -> None:
        Accounts.resume(True)
        os.execv(sys.executable, ['python'] + sys.argv) 

    def resume(condition:bool = 'return') -> bool:
        if condition == 'return':
            value =  int(DB.get(['value'],'config',"id = 'resume'")[0][0])
            return True if value == 1 else False
        else:
            print(condition,0)
            DB.update("config", {"value": condition}, f"id = 'resume'")
            return condition
