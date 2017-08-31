from hashlib import sha256
from random import choice
POSTS_PER_PAGE = 3


def make_salt():
    '''returns a salt '''
    alpha_digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([choice(alpha_digits) for x in range(16)])

def make_hash(value, salt = None):
    ''' returns value hashed and salted, and salt'''
    if not salt:
        salt = make_salt()
    hashed = sha256(str.encode(value + salt)).hexdigest()
    return '{0},{1}'.format(hashed, salt)

def check_hash(user_input, hash_db):
    '''returns True if both values are equal'''
    salt = hash_db.split(',')[1]
    if make_hash(user_input, salt) == hash_db:
        return True
    else:
        return False
