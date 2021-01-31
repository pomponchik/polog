import time
import pytest
from polog import flog, config
from polog.handlers.memory.saver import memory_saver


handler = memory_saver()
config.add_handlers(handler)

@flog(message='base text')
def function():
    return True

def test_empty():
    """
    Проверяем, что лог через flog записывается.
    """
    function()
    time.sleep(0.0001)
    log = handler.last
    assert log.fields['module'] == test_empty.__module__
    assert log.fields['function'] == function.__name__

def test_message():
    """
    Проверяем, что сообщение по умолчанию записывается.
    """
    function()
    time.sleep(0.0001)
    log = handler.last
    message = log.fields['message']
    assert message == 'base text'
