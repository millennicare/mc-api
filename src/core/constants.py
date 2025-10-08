import re

PASSWORD_ERROR_MESSAGE = "Password must be 8-64 characters long, contain at least one uppercase letter, and one special character (!@#$%^&*)."
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,64}$")
