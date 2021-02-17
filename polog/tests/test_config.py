import pytest
from polog import config
from polog.core.base_settings import BaseSettings


def test_set_valid_key_delay_before_exit():
    """
    Проверяем, что настройка с корректным ключом принимается и сохраняется в BaseSettings.
    """
    # delay_before_exit
    config.set(delay_before_exit=1)
    assert BaseSettings().delay_before_exit == 1
    config.set(delay_before_exit=2)
    assert BaseSettings().delay_before_exit == 2
    # service_name
    config.set(service_name='lol')
    assert BaseSettings().service_name == 'lol'
    config.set(service_name='kek')
    assert BaseSettings().service_name == 'kek'
    # level
    config.set(level=1)
    assert BaseSettings().level == 1
    config.set(level=2)
    assert BaseSettings().level == 2
    config.set(level=1)
    # errors_level
    config.set(errors_level=1)
    assert BaseSettings().errors_level == 1
    config.set(errors_level=2)
    assert BaseSettings().errors_level == 2
    # original_exceptions
    config.set(original_exceptions=True)
    assert BaseSettings().original_exceptions == True
    config.set(original_exceptions=False)
    assert BaseSettings().original_exceptions == False
    config.set(original_exceptions=True)
    # pool_size
    config.set(pool_size=1)
    assert BaseSettings().pool_size == 1
    config.set(pool_size=2)
    assert BaseSettings().pool_size == 2

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

def test_set_invalid_value():
    """
    Проверяем, что значение настройки с неправильным типом данных использовать не получется и поднимется исключение.
    """
    try:
        config.set(delay_before_exit='lol')
        assert False
    except TypeError:
        assert True
    except:
        assert False
