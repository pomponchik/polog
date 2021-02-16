import time
import asyncio
import pytest
from polog import flog


@flog(message='base text')
def function():
    return True

@flog(message='base text 2')
@flog(message='base text')
def function_2():
    return True

@flog(message='base text')
async def function_3():
    return True

@flog
def function_4():
    return True

def test_empty(handler):
    """
    Проверяем, что лог через flog записывается.
    """
    handler.clean()
    function()
    time.sleep(0.0001)
    log = handler.last
    assert log is not None
    assert log['module'] == test_empty.__module__
    assert log['function'] == function.__name__

def test_empty_async(handler):
    """
    Проверяем, что лог через flog записывается (для корутин).
    """
    handler.clean()
    asyncio.run(function_3())
    time.sleep(0.0001)
    log = handler.last
    assert log is not None
    assert log['module'] == test_empty.__module__
    assert log['function'] == function_3.__name__

def test_message(handler):
    """
    Проверяем, что сообщение по умолчанию записывается.
    """
    handler.clean()
    function()
    time.sleep(0.0001)
    message = handler.last['message']
    assert message == 'base text'

def test_double(handler):
    """
    Проверка, что при двойном декорировании запись генерится только одна.
    """
    handler.clean()
    function_2()
    time.sleep(0.0001)
    assert len(handler.all) == 1
    assert handler.last['message'] == 'base text 2'

def test_working():
    """
    Проверяем, что декоратор не ломает поведение функции.
    """
    assert function() == True

def test_working_without_brackets():
    """
    Проверяем, декоратор можно вызывать без скобок и функция остается рабочей.
    """
    assert function_4() == True
