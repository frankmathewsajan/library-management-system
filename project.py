import base64
from datetime import datetime
import sys
import PySimpleGUI as sg
import requests
from PIL import Image
import io
import socket
import random

from classes.Layouts import Layouts
from classes.Accounts import Accounts
from classes import MAX_QUERIES, TITLE, THEME
from classes.Library import Library

sg.theme(THEME)

windows = []


def main():
    auth = Accounts.check_auth()
    layout_name = get_auth_layout_name(auth)
    if not auth and layout_name:
        auth_window = sg.Window(
            f"Authentication | {TITLE}",
            Layouts.auth_layout(layout_name),
            margins=(150, 75),
            resizable=True,
            finalize=True,
        )
        while not auth:
            event, values = auth_window.read()
            if event == "-GRESET-":
                auth_window.close()
                layout_name = "RESET"
                reset_layout = sg.Window(
                    f"Reset Password | {TITLE}",
                    Layouts.auth_layout(layout_name),
                    margins=(150, 75),
                    resizable=True,
                    finalize=True,
                )
                while True:
                    event, values = reset_layout.read()
                    if event in (sg.WIN_CLOSED, "Exit"):
                        Accounts.resume(False)
                        reset_layout.close()
                        break
                    handle_auth(event, values, auth_window)
            if event in (sg.WIN_CLOSED, "Exit"):
                break

            auth = handle_auth(event, values, auth_window)

        auth_window.close()
    if auth and layout_name:
        layout = Layouts.main_layout()
        main_window = sg.Window(
            f"Home | {TITLE}",
            layout,
            margins=(150, 75),
            resizable=True,
            finalize=True,
        )

        while True:
            event, values = main_window.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                Accounts.resume(False)
                main_window.close()
                break
            handle_main(event, values, main_window)
        sys.exit()


def api_call(query: str) -> dict:
    """
    Searches the given query on Google Books API and returns the data as JSON (dict)

    Raises:
        RuntimeError: If API call fails for any reason.
    """

    try:
        log("api_call", f"query = {query}")
        response = requests.get(
            f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={MAX_QUERIES}",
            timeout=3,
        )
        response.raise_for_status()

        log("api_call", f"data = {not not response}")
        return response.json()

    except requests.exceptions.Timeout as e:
        log("api_call", f"{e} : Timeout")
        raise RuntimeError("API call timed out") from e

    except requests.exceptions.RequestException as e:
        log("api_call", f"{e}")
        raise RuntimeError("API call failed") from e

    except socket.gaierror as e:
        log("api_call", f"{e} : Network error")
        raise RuntimeError(
            "Network error, please check your internet connection"
        ) from e


def handle_search(event, values, main_window, get_offline_data=False):
    status = Accounts.block(2)
    if status == True:
        sg.popup_error(
            "Services blocked, pay the debt to get unblocked.", title="Restrict"
        )
        return False

    search_window = sg.Window(
        TITLE,
        Layouts.search_layout(),
        resizable=True,
        finalize=True,
        margins=(150, 75),
    )
    windows.append(search_window)
    while True:
        event, values = search_window.read()
        if event in ("Exit", sg.WIN_CLOSED):
            Accounts.Refresh()
            break

        elif event == "-List-":
            text = values["-List-"][0]
            search_window["-Search-"].update(text)
            search_window["-List-"].update(visible=False)

        if event == "Search":
            suggestions = Accounts.searches()
            search = values["-Search-"].strip().lower()
            search_window["-List-"].update(suggestions)
            search_window["-List-"].update(visible=True)
            log(
                "handle_search",
                f"Searching for {search} : Offline = {get_offline_data}",
            )
            try:

                if search and search in Library.searches():
                    log("handle_search", f"Searching for {search} in DB")
                    book_info = Library.books(
                        ["title", "author", "uid"], "search", search
                    )
                    file_list = [
                        f"{title} by {decode(author)}" for title, author, _ in book_info
                    ]
                elif search:
                    data = api_call(search) if not get_offline_data else False
                    if data:
                        log("handle_search", f"Searching for {search} in 'api_call'")
                        book_info = Library.set_books(data, search)
                    else:
                        log("handle_search", f"Showing all books in DB")
                        sg.popup("No Internet Search: Showing All Offline Books")
                        book_info = Library.books(["title", "author", "uid"])
                    log("handle_search.book_info_0", book_info)
                    file_list = [
                        f"{title} by {decode(author)}" for title, author, _ in book_info
                    ]
                    log("handle_search.file_list_0", file_list)
                    random.shuffle(file_list)
                else:
                    sg.popup("Search something!")
                    file_list = []
            except BaseException as e:
                log("handle_search.BaseException", e)
                file_list = []
            log("handle_search.book_info", book_info)
            log("handle_search.file_list", file_list)
            search_window["-BOOK LIST-"].update(file_list)
        elif event == "-BOOK LIST-":
            book_name = values["-BOOK LIST-"]
            log("handle_search.book_name", book_name)
            log("handle_search.book_info_2", book_info)
            uid = next(
                filter(
                    lambda book_tuple: f"{book_tuple[0]} by {decode(book_tuple[1])}"
                    == book_name[0],
                    book_info,
                )
            )[2]

            try:
                connectivity = (
                    True
                    if socket.create_connection(("8.8.8.8", 53), timeout=3)
                    else False
                )
            except Exception as e:
                connectivity = False

            edit_preview(uid, search_window, connectivity)
        handle_checkout(event, values)


def handle_transaction(_, values, main_window):
    try:
        amount = int(values["-ADD_AMOUNT-"].strip())
    except ValueError:
        amount = 0
    new_balance = Accounts.add_money(amount)
    main_window["-ADD_AMOUNT-"].update(0)
    main_window["-BALANCE-"].update(new_balance)


def handle_checkout(event, values) -> None:
    uid = values["-UID-"]
    if event == "-BORROW-":
        Accounts.checkout_book(uid)
    elif event == "-BUYB-":
        Accounts.purchase_book(uid)


def get_png_data(url: str, uid: str, connectivity: bool) -> str:
    image_data = Library.books(["image_data"], "uid", uid)[0][0]
    if image_data:
        return image_data

    elif connectivity:
        try:
            response = requests.get(url, timeout=3, stream=True)
            response.raise_for_status()

            with Image.open(response.raw) as image:
                image_bytes = io.BytesIO()
                image.save(image_bytes, format="PNG")
                image_data = image_bytes.getvalue()
                Library.set_image(uid, image_data)

            return image_data

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch image: {e}")
            return None


def edit_preview(uid: str, search_window, connectivity: bool):
    (
        title,
        author,
        url,
        description,
        pgno,
        type_,
        publisher,
        sale,
        price,
    ) = Library.books(
        [
            "title",
            "author",
            "imageLinks",
            "description",
            "pgno",
            "type",
            "publisher",
            "saleability",
            "price",
        ],
        "uid",
        uid,
    )[
        0
    ]

    author = decode(author) if author else None
    publisher = decode(publisher) if publisher else None
    description = decode(description) if description else None

    search_window["-TITLE-"].update(f"Book : {title} by {author}")
    search_window["-UID-"].update(uid)
    search_window["-DESC-"].update(description)
    search_window["-PGNO-"].update(f"No of Pages : {pgno}")
    search_window["-TYPE-"].update(f"Audience : {type_}")
    search_window["-PUB-"].update(f"Publisher : {publisher}")
    search_window["-IMAGE-"].update(data=get_png_data(url, uid, connectivity))

    toggle_elements(["-BORROW-"], True, search_window)

    if sale:
        search_window["-BUY-"].update(f"₹{price}")
        toggle_elements(["-BUY-", "-BUYB-"], True, search_window)
    else:
        toggle_elements(["-BUY-", "-BUYB-"], False, search_window)


def toggle_elements(l, visibility: bool, window):
    if l:
        for e in l:
            window[e].update(visible=visibility)


def handle_auth(event, values, window=None) -> bool:
    username = values["username"].strip()
    password = values["password"].strip()
    if event == "-LOGIN-":
        return Accounts.login(username, password, window)
    elif event == "-REGISTER-":
        return Accounts.register(username, password, window)
    elif event == "-RESET-":
        confirm_password = values["confirm_password"].strip()
        if password == confirm_password:
            return Accounts.reset_password(username, password)
        else:
            window["-MESSAGE-"].update("Passwords doesn't match", text_color="red")
            return False


def handle_main(event, values, window):
    if event == "Logout":
        Accounts.logout()
        sys.exit()
    elif event == "Refresh":
        Accounts.Refresh()
    elif event == "Full Screen":
        window.Maximize()
    elif event == "Reset Password":
        layout_name = "RESET"
        reset_layout = sg.Window(
            f"Reset Password | {TITLE}",
            Layouts.auth_layout(layout_name),
            margins=(150, 75),
            resizable=True,
            finalize=True,
        )
        while True:
            event, values = reset_layout.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                Accounts.resume(False)
                reset_layout.close()
                break
            handle_auth(event, values)
    elif event == "Delete Account":
        if (
            sg.popup_ok_cancel(
                "Are you sure ? This cannot be reversed",
                title="DELETE ACCOUNT",
                text_color="red",
            )
            == "OK"
        ):
            Accounts.delete()
    elif event == "Search NEW Books":
        handle_search(event, values, window)
    elif event == "See Available Books":
        handle_search(event, values, window, True)
    elif event == "Add Money":
        handle_transaction(event, values, window)
    elif "book_" in event:
        uid = event.split("book_")[1]
        Accounts.return_book(uid)


def get_auth_layout_name(auth: bool = False) -> str | None:
    if Accounts.resume():
        return True
    ask_window = sg.Window(
        f"Welcome | {TITLE}",
        Layouts.ask_layout(auth),
        margins=(150, 75),
        resizable=True,
        finalize=True,
    )
    while True:
        event, _ = ask_window.read()
        if event == sg.WIN_CLOSED:
            ask_window.close()
            return None
        elif event == "Logout":
            Accounts.logout()
            sg.popup("Logout Successful")
            return "Login"
        elif event:
            ask_window.close()
            return event


def decode(text):
    return base64.b64decode(text).decode() if text else None


def encode(text):
    return base64.b64encode(text.encode()).decode() if text else None


def log(fn, text) -> bool:
    try:
        with open("log.txt", "a") as log:
            t = f"{text} [{fn}] [{datetime.now()}]\n"
            print(t)
            log.write(t)
        return True
    except Exception as e:
        return False


if __name__ == "__main__":
    main()
