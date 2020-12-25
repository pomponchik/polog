import pytest
from polog.errors import LoggedError, IncorrectUseOfTheDecoratorError


def test_errors_logged():
    """
    Проверяем, что исключение поднимается.
    """
    try:
        raise LoggedError
    except LoggedError:
        pass

def test_errors_incorrect_use():
    """
    Проверяем, что исключение поднимается.
    """
    try:
        raise IncorrectUseOfTheDecoratorError
    except IncorrectUseOfTheDecoratorError:
        pass
