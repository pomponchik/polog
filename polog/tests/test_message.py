import time
import pytest
from polog import flog, message, config
from polog.handlers.memory.saver import memory_saver


handler = memory_saver()
config.add_handlers(handler)

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


def test_basic():
    """Проверяем, что дефолтное сообщение подменяется новым."""
    normal_function()
    # Дожидаемся, чтобы лог успел записаться.
    time.sleep(0.0001)
    assert handler.last.fields['message'] == 'new text'

def test_basic_exception():
    """Проверяем работу с исключениями."""
    error_function()
    time.sleep(0.0001)
    assert handler.last.fields['exception_type'] == 'ValueError'
    assert handler.last.fields['exception_message'] == 'exception text'
    error_function_2()
    time.sleep(0.0001)
    assert handler.last.fields['exception_type'] == 'ValueError'
    assert handler.last.fields['exception_message'] == 'exception text 2'
    error_function_3()
    time.sleep(0.0001)
    assert handler.last.fields['exception_type'] == 'ValueError'
    assert handler.last.fields['exception_message'] == 'new message'
