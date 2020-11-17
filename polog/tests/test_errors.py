import pytest
from polog.errors import LoggedError, IncorrectUseOfTheDecoratorError


def test_errors_logged():
    try:
        raise LoggedError
    except LoggedError:
        pass

def test_errors_incorrect_use():
    try:
        raise IncorrectUseOfTheDecoratorError
    except IncorrectUseOfTheDecoratorError:
        pass
