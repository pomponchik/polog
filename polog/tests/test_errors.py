from polog.errors import LoggedError, IncorrectUseOfTheDecoratorError
import pytest

def test_errors_logged():
    try:
        raise LoggedError
    except LoggedError:
        pass
