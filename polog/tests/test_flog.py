import time
import asyncio
import pytest
from polog import flog, config
from polog.handlers.memory.saver import memory_saver


handler = memory_saver()
config.add_handlers(handler)

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

def test_empty():
    """
    Проверяем, что лог через flog записывается.
    """
    handler.clean()
    function()
    time.sleep(0.0001)
    log = handler.last
    assert log is not None
    assert log.fields['module'] == test_empty.__module__
    assert log.fields['function'] == function.__name__

def test_empty_async():
    """
    Проверяем, что лог через flog записывается (для корутин).
    """
    handler.clean()
    asyncio.run(function_3())
    time.sleep(0.0001)
    log = handler.last
    assert log is not None
    assert log.fields['module'] == test_empty.__module__
    assert log.fields['function'] == function_3.__name__

def test_message():
    """
    Проверяем, что сообщение по умолчанию записывается.
    """
    handler.clean()
    function()
    time.sleep(0.0001)
    log = handler.last
    message = log.fields['message']
    assert message == 'base text'

def test_double():
    """
    Проверка, что при двойном декорировании запись генерится только одна.
    """
    handler.clean()
    function_2()
    time.sleep(0.0001)
    assert len(handler.all) == 1
    assert handler.last.fields['message'] == 'base text 2'

def test_working():
    """
    Проверяем, что декоратор не ломает поведение функции.
    """
    assert function() == True
