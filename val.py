import re

def is_empty(x):
    """checks if the string x is empty"""
    if not x:
        return True
    else:
        return False

def space(x):
    """Checks if x has space in it""" 
    if ' ' in x:
        return True
    else:
        return False

def wrong_len(x):
    """Checks x length is less than 3""" 
    if len(x) < 3:
        return True
    else:
        return False

def wrong_email(x):
    '''Checks that email contains only one period after @, one @ and'''
    
    if not re.match(r"[^@]+@[^@]+\.[^@.]+", x):
        return True
    else:
        return False

