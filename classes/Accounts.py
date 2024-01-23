from datetime import datetime, timedelta
import os
import sys
import PySimpleGUI as sg
import bcrypt
import re
from classes.Constants import (
    CHECKOUT_LIMIT,
    DUE_DAYS,
    FINE,
    PASSWORD_CONDITIONS,
    PASSWORD_REGEX,
    USERNAME_CONDITIONS,
    USERNAME_REGEX,
)

from .Database import Database as DB
DB.init()

class Accounts:
    def username() -> str:
        return DB.get(["username"], "users", f"auth = 1")[0][0]

    def searches() -> list:
        username = Accounts.username()
        tuple_list = DB.get(
            ["username", "search"],
            "searches",
            f"username = '{username}' or username = 'SYSTEM'",
        )
        return list(map(lambda tup: tup[1], tuple_list)) if tuple_list else []

    def check_auth() -> bool:
        return DB.count("users", "auth = 1") != 0

    def register(username: str, password: str, window) -> bool:
        message, valid_input = "User already exists", True
        if not re.match(USERNAME_REGEX, username) or not re.match(
            PASSWORD_REGEX, password
        ):
            if not re.match(USERNAME_REGEX, username):
                message = "Invalid username"
                sg.popup_ok(USERNAME_CONDITIONS, title="SYNTAX Message")
            else:
                message = "Invalid password"
                sg.popup_ok(PASSWORD_CONDITIONS, title="SYNTAX Message")
            valid_input = False
        user_exist = len(DB.get(["username"], "users", f"username = '{username}'")) == 0
        if user_exist and valid_input:
            window["-MESSAGE-"].update("Registration Success", text_color="green")

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            DB.insert(
                "users",
                {"username": username, "password": hashed_password, "auth": True},
            )
            DB.insert("config", {"id": username, "value": False})
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
        check_result = bcrypt.checkpw(password, user_info[0][1])
        if len(user_info) != 0 and check_result:
            window["-MESSAGE-"].update("Login Success", text_color="green")
            DB.update("users", {"auth": True}, f"username = '{username}'")
            sg.popup("Login Success")
            return True
        else:
            window["-MESSAGE-"].update("User does not exist or incorrect password")
            return False

    def logout():
        DB.update("users", {"auth": 0})
        Accounts.Refresh(False)
        sys.exit()

    def delete():
        username = Accounts.username()
        DB.delete("users", f"username = '{username}'")
        DB.delete("books", f"username = '{username}'")
        DB.update("searches", {"username": "SYSTEM"}, f"username = '{username}'")
        sg.Popup(f"Account Deleted...", title=f"SYSTEM MESSAGE", text_color="red")
        Accounts.Refresh(False)

    def reset_password(username: str, new_password: str) -> bool:
        user_info = DB.get(["username"], "users", f"username = '{username}'")
        if len(user_info) == 0:
            return False
        if not re.match(PASSWORD_REGEX, new_password):
            sg.popup_ok(PASSWORD_CONDITIONS, title="SYNTAX Message")
            return False
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        DB.update("users", {"password": hashed_password}, f"username = '{username}'")
        sg.popup("Password reset successful", title="Authentication | Passsword Reset")
        Accounts.Refresh(False)
        return True

    def borrowed(columns: list) -> list:

        result = (
            DB.join_and_get(
                [f"{col}" for col in columns],
                "library",
                "books",
                f"a.uid = b.uid",
                [f"b.username = '{Accounts.username()}'", "b.type = 'BORROWED'"],
            ),
        )
        return result

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
        from classes.Library import Library
        from project import decode

        book_name = Library.books(["title", "author"], "uid", uid)[0]
        due_date = datetime.now() + timedelta(days=10)

        ch = sg.popup_ok_cancel(
            f"Confirm Book Check Out\n\nBook Name : {book_name[0]} by {decode(book_name[1])}",
            title="Confirm Check-Out",
        )
        if not (True if ch == "OK" else False):
            return
        borrowed = list(map(lambda t: t[0], Accounts.borrowed(["a.uid"])[0]))
        username = Accounts.username()
        if uid and len(borrowed) < CHECKOUT_LIMIT and uid not in borrowed:
            DB.insert(
                "books",
                {
                    "uid": uid,
                    "type": "BORROWED",
                    "username": username,
                    "date": datetime.now(),
                },
            )

            count = (
                int(DB.get(["checked_out"], "users", f"username = '{username}'")[0][0])
                + 1
            )
            DB.update("users", {"checked_out": count}, f"username = '{username}'")
            title, msg = (
                "Success ✓✓✓",
                f"Added to Check Out List ✓, {count}/3\nDue Date : {due_date.strftime('%d-%B-%Y')}\n\nPlease return your book before due date to avoid fines.",
            )
        elif uid in borrowed:
            title, msg = "Error ×××", "Already in List ×"
        elif uid is None:
            title, msg = "Error ×××", "Please select a book from side bar ×"
        else:
            title, msg = "Error ×××", "List Already Full ×"

        sg.Popup(
            f"Name : {book_name[0]} by {decode(book_name[1])}\n\n{msg}",
            title=f"Check-Out | {title}",
            keep_on_top=True,
        )

    def add_money(amount: int) -> int:
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
        if Accounts.block(2) and balance > 0:
            Accounts.block(1)
            sg.popup_ok(
                "Your bebt is paid, so all transactions has been unblocked",
                title="Transactions Unblocked",
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

    def return_book(uid):
        from classes.Library import Library
        from project import decode

        book_name = Library.books(["title", "author"], "uid", uid)[0]
        fine, due = Accounts.fine(uid)
        ch = sg.popup_ok_cancel(
            f"Confirm Book Check In\nBook Name : {book_name[0]} by {decode(book_name[1])}\nDue Date : {due}\nFine : ₹{fine}",
            title="Confirm Check-In",
        )
        if True if ch == "OK" else False:
            username = Accounts.username()
            balance = DB.get(["balance"], "users", f"username = '{username}'")[0][0]
            if isinstance(fine, int) and 0 <= fine:
                DB.update(
                    "users", {"balance": balance - fine}, f"username = '{username}'"
                )
                balance -= fine
                sg.popup_ok(
                    f"° Amount ₹{fine} debited ✓\nCurrent Balance = ₹{balance}",
                    title="Late Check In | Transaction Message",
                )
                if balance < 0:
                    sg.popup_ok(
                        f"° Your account is in debt, Further transactions will be blocked till debts are paid.",
                        title="SYSTEM Restricted",
                        text_color="red",
                    )
            Accounts.block()
            DB.remove("books", {"uid": uid, "type": "BORROWED", "username": username})
            count = (
                int(DB.get(["checked_out"], "users", f"username = '{username}'")[0][0])
                - 1
            )
            DB.update("users", {"checked_out": count}, f"username = '{username}'")
            Accounts.Refresh(True)

    def block(block=0) -> bool:
        """
        0 - Block\n
        1 - Unblock\n
        2 - Check Status
        """
        username = Accounts.username()
        if block == 0:
            DB.update("config", {"value": True}, f"id = '{username}'")
            return True
        elif block == 1:
            DB.update("config", {"value": False}, f"id = '{username}'")
            return False
        elif block == 2:
            value = int(DB.get(["value"], "config", f"id = '{username}'")[0][0])
            print(value, type(value))
            return True if value == 1 else False

    def fine(uid):
        date = DB.join_and_get(
            ["b.date"],
            "library",
            "books",
            f"a.uid = b.uid",
            [
                f"b.uid = '{uid}'",
            ],
        )[0][0]

        date_object = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        current_date = datetime.now()
        due = (date_object + timedelta(days=10)).strftime("%Y-%B-%d")
        amount = max(0, int((current_date - date_object).days - DUE_DAYS)) * FINE

        return (amount, due)

    def Refresh(resume: bool = True) -> None:
        Accounts.resume(resume)
        os.execv(sys.executable, ["python"] + sys.argv)

    def resume(condition: bool = "return") -> bool:
        if condition == "return":
            value = int(DB.get(["value"], "config", "id = 'resume'")[0][0])
            return True if value == 1 else False
        else:
            DB.update("config", {"value": condition}, f"id = 'resume'")
            return condition
