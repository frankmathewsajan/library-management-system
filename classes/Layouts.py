import PySimpleGUI as sg

from classes.Accounts import Accounts
from .Constants import TITLE

class Layouts:
    """
    Manages layouts.

    * Stores layouts (name: data) in `self.layouts`.
    * `get_layout`: Retrieve layout by name (returns None if not found).
    * `set_layout`: Store new or update existing layouts.
    """

    def auth_layout(login): return [
        [sg.Text(login)],
        [sg.HorizontalSeparator()],
        [sg.Text('Username', size=(15, 1)), sg.InputText(key='-USERNAME-')],
        [sg.Text('Password', size=(15, 1)), sg.InputText(key='-PASSWORD-',password_char='*')],
        [sg.Submit(key=f'-{login.upper()}-')],
        [[sg.Text('...', size=(30, 1),key='-MESSAGE-', text_color='red')]]
    ]

    def ask_layout(auth:bool = False): 
        if auth:
            return [[sg.Button(f'Continue as {Accounts.username()}'), sg.Button('Logout')]]

        else:
            return [[sg.Button('Login'), sg.Button('Register')]]
