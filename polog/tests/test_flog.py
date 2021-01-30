import time
import pytest
from polog import flog, config


lst = []
add_item = lambda *args, **kwargs: lst.append(([x for x in args], {x: y for x, y in kwargs.items()}))
config.add_handlers(add_item)

@flog(message='base text')
def function():
    return True

def test_empty():
    """
    Проверяем, что лог через flog записывается.
    """
    function()
    time.sleep(0.0001)
    log = lst[len(lst) - 1][1]
    assert log['module'] == test_empty.__module__
    assert log['function'] == function.__name__
    lst.pop()

def test_message():
    """
    Проверяем, что сообщение по умолчанию записывается.
    """
    function()
    time.sleep(0.0001)
    log = lst[len(lst) - 1][1]
    message = log['message']
    assert message == 'base text'
    lst.pop()
