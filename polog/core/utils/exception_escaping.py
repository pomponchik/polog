from functools import wraps


def exception_escaping(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            pass
    return wrapper
