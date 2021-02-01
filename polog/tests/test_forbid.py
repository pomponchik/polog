import time
import pytest
from polog import flog, logging_is_forbidden, config
from polog.handlers.memory.saver import memory_saver


handler = memory_saver()
config.add_handlers(handler)

@logging_is_forbidden
@flog(message='base text', level=100)
def function():
    pass

@flog(message='base text', level=100)
@logging_is_forbidden
def function_2():
    pass

@flog(message='base text', level=100)
@flog(message='base text', level=100)
@flog(message='base text', level=100)
@logging_is_forbidden
@flog(message='base text', level=100)
@flog(message='base text', level=100)
@flog(message='base text', level=100)
def function_3():
    pass


def test_before():
    handler.clean()
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_after():
    handler.clean()
    function_2()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_multiple():
    handler.clean()
    function_3()
    time.sleep(0.0001)
    assert len(handler.all) == 0
