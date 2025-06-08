import re

class Validation():
    def __init__(self) -> None:
        pass

    def is_valid_email(self, email):
        pattern = '^[a-zA-Z0-9 .+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
    
    def is_valid_password(self, password):
        if (
            len(password) < 8
            or not any(c.isdigit() for c in password)
            or not any(c.islower() for c in password)
            or not any(c.isupper() for c in password)
            or not any(c in "!@#$%^&*()-_=+[{]}\|;:'\",<.>/?`~" for c in password)
        ):
            return False
        return True

    
    

