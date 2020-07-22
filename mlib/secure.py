from random import choice, randint
import string
def gen_password():
    # import string
    # from random import *
    characters = string.ascii_letters + string.punctuation + string.digits
    password = "".join(choice(characters) for x in range(randint(8, 16)))
    password = password.replace('\\',
                                '/')  # wolfram hated the \ character and thought it was some weird escape sequence
    return password
