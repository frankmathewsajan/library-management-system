AUTH = False
TITLE = "Harvard Central Library"
THEME = "TanBlue"
ADMIN_PASS = b"$2b$12$RfGCPEzC5GwCCcnmpDIBhuZnZItstycBgpQWEqz/bqYcOJzsB9D9C"

USERNAME_REGEX = r"^[a-zA-Z0-9]{3,20}$"
USERNAME_CONDITIONS = '''
Username Conditions
1. Be between 3 to 20 characters with no space in between.
2. Consist of only capital and small letters and numbers.
3. Not be only numbers
'''
PASSWORD_REGEX = r"^(?=.*\d)(?=.*[a-zA-Z])(?=.*[^\w\s]).{8,20}$"
PASSWORD_CONDITIONS = '''
Password Conditions 
1. Be between 8 to 20 characters.
2. Be combination of letters, digits and special characters.
3. Atleast one digit, one alphabet and a special character (0-9A-Za-z ~!@#$%^&*).
'''
CHECKOUT_LIMIT = 3
DUE_DAYS = 10
FINE = 10
MAX_QUERIES = 10
