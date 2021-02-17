import pytest
from polog import config
from polog.core.base_settings import BaseSettings


def test_set_valid_key_delay_before_exit():
    """
    Проверяем, что настройка с корректным ключом принимается и сохраняется в BaseSettings.
    """
    config.set(delay_before_exit=1)
    assert BaseSettings().delay_before_exit == 1
    config.set(delay_before_exit=2)
    assert BaseSettings().delay_before_exit == 2

def test_set_invalid_key():
    """
    Проверяем, что неправильный ключ настройки использовать не получется и поднимется исключение.
    """
    try:
        config.set(invalid_key='lol')
        assert False
    except KeyError:
        assert True
    except:
        assert False
