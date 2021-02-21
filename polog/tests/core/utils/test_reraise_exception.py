import pytest
from polog.core.utils.reraise_exception import reraise_exception
from polog import config, LoggedError


def test_raise_original():
    """
    При настройке original_exceptions=True переподниматься должно оригинальное исключение.
    """
    config.set(original_exceptions=True)
    try:
        raise ValueError
    except Exception as e:
        try:
            reraise_exception(e)
            assert False # Проверка, что исключение в принципе переподнимается.
        except Exception as e2:
            assert e is e2

def test_raise_not_original():
    """
    При настройке original_exceptions=False переподниматься должно исключение LoggedError.
    """
    config.set(original_exceptions=False)
    try:
        raise ValueError
    except Exception as e:
        try:
            reraise_exception(e)
            assert False # Проверка, что исключение в принципе переподнимается.
        except LoggedError as e2:
            assert True
        except Exception as e2:
            assert False
