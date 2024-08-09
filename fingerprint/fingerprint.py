import random
import string

class main:
    def generate():
        '''return random string composed of 8 characters randomly selected from a-z, 0-9'''
        characters = string.ascii_lowercase + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(8))
        return random_string