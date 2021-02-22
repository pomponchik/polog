import time
import pytest
from polog import flog, message, field, config


@flog(message='base text')
def normal_function():
    message('new text', level=5)
    return True

@flog(message='base text')
def error_function():
    try:
        raise ValueError('exception text')
    except ValueError as e:
        message(e=e)

@flog(message='base text')
def error_function_2():
    try:
        raise ValueError('exception text 2')
    except ValueError as e:
        message(exception=e)

@flog(message='base text')
def error_function_3():
    message(exception_type='ValueError', exception_message='new message')


def test_basic(handler):
    """Проверяем, что дефолтное сообщение подменяется новым."""
    normal_function()
    # Дожидаемся, чтобы лог успел записаться.
    time.sleep(0.0001)
    assert handler.last['message'] == 'new text'

def test_basic_exception(handler):
    """Проверяем работу с исключениями."""
    error_function()
    time.sleep(0.0001)
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'exception text'
    error_function_2()
    time.sleep(0.0001)
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'exception text 2'
    error_function_3()
    time.sleep(0.0001)
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'new message'

def test_affects(handler):
    """
    Пробуем зааффектить одним вызовом message() другой.
    """
    handler.clean()
    def function_without_flog():
        message('lol', local_variables='kek')
    @flog()
    def function_with_flog():
        message('lolkek')
    function_without_flog()
    function_with_flog()
    time.sleep(0.0001)
    assert handler.last['local_variables'] is None

def test_another_field(handler):
    """
    Проверяем, что работает прописывание собственных значений для пользовательских полей.
    """
    handler.clean()
    def extractor(a, **b):
        pass
    config.add_fields(lolkek=field(extractor))
    @flog
    def function():
        message('lolkek', lolkek='lolkek')
    function()
    time.sleep(0.0001)
    assert handler.last['lolkek'] == 'lolkek'
