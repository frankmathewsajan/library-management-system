import PySimpleGUI as sg

from classes.Accounts import Accounts
from classes.Database import Database

from .Constants import TITLE


class Layouts:
    """
    Manages layouts.

    * Stores layouts (name: data) in `self.layouts`.
    * `get_layout`: Retrieve layout by name (returns None if not found).
    * `set_layout`: Store new or update existing layouts.
    """

    def auth_layout(login) -> list:
        return [
            [sg.Text(login)],
            [sg.HorizontalSeparator()],
            [sg.Text("Username", size=(15, 1)), sg.InputText(key="-USERNAME-")],
            [
                sg.Text("Password", size=(15, 1)),
                sg.InputText(key="-PASSWORD-", password_char="*"),
            ],
            [sg.Submit(key=f"-{login.upper()}-")],
            [[sg.Text("...", size=(30, 1), key="-MESSAGE-", text_color="red")]],
        ]

    def ask_layout(logged_in: bool = False) -> list:
        if logged_in:
            return [
                [sg.Button(f"Continue as {Accounts.username()}"), sg.Button("Logout")]
            ]

        else:
            return [[sg.Button("Login"), sg.Button("Register")]]

    def search_layout() -> list:
        book_list_col = [
            [sg.T("Book Search")],
            [
                sg.InputText(size=(25, 1), enable_events=True, key="-Search-"),
                sg.Button("Search"),
            ],
            [
                sg.Listbox(
                    values=[], enable_events=True, size=(60, 10), key="-BOOK LIST-"
                )
            ],
        ]
        preview_col = [
            [
                sg.T(size=(50, 1), key="-TITLE-"),
                sg.InputText(size=(1, 1), key="-UID-", visible=False),
            ],
            [sg.Image(key="-IMAGE-"), sg.T(size=(40, 10), key="-DESC-")],
            [
                sg.T(size=(18, 2), key="-PGNO-"),
                sg.T(size=(18, 2), key="-PUB-"),
                sg.T(size=(16, 2), key="-TYPE-"),
            ],
            [sg.HSep()],
            [
                sg.B("CHECK OUT", size=(17, 2), key="-BORROW-"),
                sg.VSep(),
                sg.T(f"₹0", key="-BUY-", visible=False),
                sg.B("Buy", size=(15, 1), key="-BUYB-", visible=False),
            ],
        ]
        search_layout = [
            [
                sg.Column(book_list_col),
                sg.VSeperator(),
                sg.Column(preview_col),
            ]
        ]
        return search_layout

    def available_layout() -> list:
        book_list_col = [
            [sg.T("Book Search")],
            [
                sg.InputText(size=(25, 1), enable_events=True, key="-Search-"),
                sg.Button("Search"),
            ],
            [
                sg.Listbox(
                    values=[], enable_events=True, size=(60, 10), key="-BOOK LIST-"
                )
            ],
        ]
        preview_col = [
            [
                sg.T(size=(50, 1), key="-TITLE-"),
                sg.InputText(size=(1, 1), key="-UID-", visible=False),
            ],
            [sg.Image(key="-IMAGE-"), sg.T(size=(40, 10), key="-DESC-")],
            [
                sg.T(size=(18, 2), key="-PGNO-"),
                sg.T(size=(18, 2), key="-PUB-"),
                sg.T(size=(16, 2), key="-TYPE-"),
            ],
            [sg.HSep()],
            [
                sg.B("CHECK OUT", size=(17, 2), key="-BORROW-"),
                sg.VSep(),
                sg.T(f"₹0", key="-BUY-", visible=False),
                sg.B("Buy", size=(15, 1), key="-BUYB-", visible=False),
            ],
        ]
        search_layout = [
            [
                sg.Column(book_list_col),
                sg.VSeperator(),
                sg.Column(preview_col),
            ]
        ]
        return search_layout

    def main_layout() -> list:
        borrowed = Accounts.borrowed(["image_data"])
        image_holders = [sg.Image(data=data, size=(100, 125)) for data in borrowed]
        users = Database.get(["username", "checked_out", "purchased"], "users")
        balance = Database.get(
            ["balance"], "users", f"username = '{Accounts.username()}'"
        )[0][0]
        headrow_members = ["Name", "Checked Out", "Purchased"]
        rows_members = [[t[0], t[1], t[2]] for t in users]
        member_list = [
            sg.Table(
                values=rows_members,
                headings=headrow_members,
                auto_size_columns=True,
                display_row_numbers=False,
                justification="center",
                key="-TABLE-",
                enable_events=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
            )
        ]

        purchase_book = Database.join_and_get(
            ["a.title", "a.author", "a.price"],
            "library",
            "books",
            f"a.uid = b.uid",
            [f"b.username = '{Accounts.username()}'", "b.type = 'PURCHASED'"],
        )
        headrow_books = ["Name", "Author", "Price"]
        rows_books = [[t[0], t[1], t[2]] for t in purchase_book]
        purchase_list = [
            sg.Table(
                values=rows_books,
                headings=headrow_books,
                auto_size_columns=True,
                display_row_numbers=False,
                justification="center",
                key="-TABLE-",
                size=(15, 3),
                enable_events=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
            )
        ]

        borrow_book = Database.join_and_get(
            ["a.title", "a.author", "a.uid"],
            "library",
            "books",
            f"a.uid = b.uid",
            [f"b.username = '{Accounts.username()}'", "b.type = 'BORROWED'"],
        )
        headrow_books = ["Name", "Author", "Return"]
        rows_books = [[t[0], t[1], t[2]] for t in borrow_book]
        borrow_list = [
            sg.Table(
                values=rows_books,
                headings=headrow_books,
                auto_size_columns=True,
                size=(15, 4),
                display_row_numbers=False,
                justification="center",
                key="-TABLE-",
                enable_events=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
            )
        ]
        return [
            [
                sg.Column(
                    [
                        [sg.T(f"CHECK-OUTS", size=(25, 1))],
                        image_holders,
                        [sg.HSep()],
                        [sg.HSep()],
                        [sg.T("TRANSACTIONS", size=(25, 1))],
                        [sg.In(size=(25, 1), key="-ADD_AMOUNT-")],
                        [
                            sg.B(
                                "Add Money",
                            )
                        ],
                        [
                            sg.T("BALANCE:", size=(8, 1)),
                            sg.T(f"{balance}", size=(6, 1), key="-BALANCE-"),
                        ],
                        [sg.HSep()],
                        [sg.HSep()],
                        [sg.T("LIBRARY", size=(25, 1))],
                        [
                            sg.B(
                                "Search NEW Books",
                            ),
                            sg.B(
                                "See Available Books",
                            ),
                        ],
                        [
                            sg.B(
                                "Full Screen",
                            ),
                            sg.B(
                                "Logout",
                            ),
                            sg.B("Refresh"),
                            sg.B("Delete Account", button_color="red"),
                        ],
                    ],
                ),
                sg.VSep(),
                sg.Column(
                    [
                        [sg.T("CHECKED OUT", size=(15, 1))],
                        borrow_list,
                        [sg.HSep()],
                        [sg.HSep()],
                        [sg.T("PURCHASED", size=(10, 1))],
                        purchase_list,
                        [sg.HSep()],
                        [sg.HSep()],
                        [sg.T(f"MEMBERS", size=(10, 1))],
                        member_list,
                    ]
                ),
            ]
        ]
