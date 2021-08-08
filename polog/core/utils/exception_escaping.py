from functools import wraps


def exception_escaping(func):
    """
    Декоратор для подавления любых исключений.

    Применять с осторожностью и только по отношению к пользовательским функциям. Недопустимо экранировать внутренние ошибки Polog.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            pass
    return wrapper
