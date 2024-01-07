import PySimpleGUI as sg

from classes.Layouts import Layouts
from classes.Accounts import Accounts
from classes.Constants import AUTH, TITLE, THEME

sg.theme(THEME)

def main():
    auth = Accounts.check_auth()

    layout = get_layout_name(auth)
    if not auth and layout:
        auth_window = sg.Window(
            f"Authentication | {TITLE}",
            Layouts.auth_layout(layout),
            margins=(150, 75),
        )
        while not auth:
            event, values = auth_window.read()
            if event in (sg.WIN_CLOSED,'Exit'):
                break
            auth = handle_auth(event, values, auth_window)
        auth_window.close()


def handle_auth(event, values, auth_window):
    if event == "-LOGIN-":
        username = values["-USERNAME-"].strip()
        password = values["-PASSWORD-"].strip()
        Accounts.login(username, password, auth_window)
    elif event == "-REGISTER-":
        username = values["-USERNAME-"].strip()
        password = values["-PASSWORD-"].strip()
        Accounts.register(username, password, auth_window)

def get_layout_name(auth:bool = False) -> str|None:
    ask_window = sg.Window(
        f"Welcome | {TITLE}",
        Layouts.ask_layout(auth),
        margins=(150, 75),
    )
    while True:
        event, _ = ask_window.read()
        if event == sg.WIN_CLOSED:
            ask_window.close()
            return None
        elif event == 'Logout':
            Accounts.logout()
            sg.popup("Logout Successful")
            return 'Login'
        elif event:
            ask_window.close()
            return event # Returns Event 'Login' or 'Register'


if __name__ == "__main__":
    main()
