import time
import pytest
from polog import flog, logging_is_forbidden


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
    return True


def test_before(handler):
    """
    Проверяем ситуацию, когда @logging_is_forbidden стоит до логирующего декоратора.
    """
    handler.clean()
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_after(handler):
    """
    Когда @logging_is_forbidden после логирующего декоратора.
    """
    handler.clean()
    function_2()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_multiple(handler):
    """
    Когда логирующие декораторы по нескольку штук с обеих сторон от @logging_is_forbidden.
    """
    handler.clean()
    function_3()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_working():
    """
    Проверяем, что декоратор не ломает поведение функции.
    """
    assert function_3() == True
