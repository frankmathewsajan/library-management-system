AUTH = False
TITLE = "Harvard Central Library"
THEME = "TanBlue"
ADMIN_PASS = b"$2b$12$RfGCPEzC5GwCCcnmpDIBhuZnZItstycBgpQWEqz/bqYcOJzsB9D9C"

USERNAME_REGEX = r"^[a-zA-Z0-9]{3,20}$"
PASSWORD_REGEX = r"^(?=.*\d)(?=.*[a-zA-Z])(?=.*[^\w\s]).{8,20}$"
CHECKOUT_LIMIT = 3
DUE_DAYS = 7
FINE = 100
