import re

PASSWORD_ERROR_MESSAGE = "Password must be 8-64 characters long, contain at least one uppercase letter, and one special character (!@#$%^&*)."
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,64}$")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
SESSION_EXPIRE_DAYS = 30
VERIFICATION_CODE_EXPIRE_MINUTES = 15
