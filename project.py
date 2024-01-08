import sys
import PySimpleGUI as sg
import requests
from PIL import Image
import io
import random

from classes.Layouts import Layouts
from classes.Accounts import Accounts
from classes.Constants import TITLE, THEME
from classes.Library import Library

sg.theme(THEME)


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
                break
            handle_main(event, values, main_window)
        main_window.close()


def api_call(query: str) -> dict:
    try:
        response = requests.get( f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10", timeout=5)
    except requests.exceptions.Timeout:
        return False
    return response.json()


def handle_search(event, values, main_window, available=False):
    search_window = sg.Window(
        TITLE,
        Layouts.search_layout(),
        resizable=True,
        finalize=True,
        margins=(150, 75),
    )
    while True:
        event, values = search_window.read()
        if event in ("Exit", sg.WIN_CLOSED):
            Accounts.Refresh()
            break
        if event == "Search":
            search = values["-Search-"].strip().lower()
            try:
                data = api_call(search) if available == False else False
                print(data,search)
                if search and search in Library.searches():
                    book_info = Library.books(
                        ["title", "author", "uid"], "search", search
                    )
                    file_list = [
                        f"{title} by {author}" for title, author, _ in book_info
                    ]
                elif search:
                    if data:
                        book_info = Library.set_books(data, search)
                    else:
                        sg.popup('No Internet: Showing Offline Data') if available == False else ''
                        book_info = Library.books(["title", "author","uid"])
                    file_list = [f"{title} by {author}" for title, author, _ in book_info]
                    random.shuffle(file_list)
                else:
                    sg.popup('Search something!') 
                    file_list = []   
            except BaseException:
                file_list = []
            search_window["-BOOK LIST-"].update(file_list)
        elif event == "-BOOK LIST-":
            book_name = values["-BOOK LIST-"]
            uid = next(filter(lambda e: f"{e[0]} by {e[1]}" == book_name[0], book_info))[2]
            edit_preview(uid, search_window, connectivity=(data is not False))
        handle_checkout(event,values)

def handle_transaction(_, values, main_window):
    print(0)
    try:
        amount = int(values["-ADD_AMOUNT-"].strip())
    except ValueError:
        amount = 0
    new_balance = Accounts.add_money(amount)
    main_window["-ADD_AMOUNT-"].update(0)
    main_window["-BALANCE-"].update(new_balance)
        

def handle_checkout(event, values)->None:
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

def edit_preview(uid: str, search_window, connectivity:bool):
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
        ], "uid", uid)[0]
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


def handle_auth(event, values, window) -> bool:
    username = values["-USERNAME-"].strip()
    password = values["-PASSWORD-"].strip()
    if event == "-LOGIN-":
        return Accounts.login(username, password, window)
    elif event == "-REGISTER-":
        return Accounts.register(username, password, window)


def handle_main(event, values, window):
    if event == "Logout":
        Accounts.logout()
        sys.exit()
    elif event == "Refresh":
        Accounts.Refresh()    
    elif event == "Full Screen":
        window.Maximize()
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
    elif event == 'Add Money':
        handle_transaction(event,values,window)      

def get_auth_layout_name(auth: bool = False) -> str | None:
    print(Accounts.resume())
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
            return event  # Returns Event 'Login' or 'Register'


if __name__ == "__main__":
    main()
