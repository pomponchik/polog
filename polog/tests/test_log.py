import time
import pytest
from polog import log, config
from polog.handlers.memory.saver import memory_saver


handler = memory_saver()
config.add_handlers(handler)


def test_base():
    """
    Проверка, что в базовом случае лог записывается.
    """
    handler.clean()
    log('lol')
    time.sleep(0.0001)
    assert handler.last is not None

def test_exception():
    """
    Проверка, что из исключения извлекается вся нужная инфа.
    """
    handler.clean()
    try:
        raise ValueError('kek')
    except ValueError as e:
        log('lol', exception=e)
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last.fields['exception_type'] == 'ValueError'
    assert handler.last.fields['exception_message'] == 'kek'

def test_level():
    """
    Проверка, что указанный уровень лога срабатывает.
    """
    handler.clean()
    log('lol', level=100)
    time.sleep(0.0001)
    assert handler.last.fields['level'] == 100

def test_function():
    """
    Проверка, что из поданной функции автоматически извлекается имя функции и имя модуля.
    """
    def function():
        pass
    handler.clean()
    log('lol', function=function)
    time.sleep(0.0001)
    assert handler.last.fields['function'] == function.__name__
    assert handler.last.fields['module'] == function.__module__

def test_raise():
    """
    Проверка, что при неправильно поданном типе именованной переменной возникает исключение.
    """
    handler.clean()
    try:
        log('lol', function=1)
        assert False
    except ValueError:
        pass
