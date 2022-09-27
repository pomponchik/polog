import time

import pytest

from polog import flog, unlog, config
from polog.errors import IncorrectUseOfTheDecoratorError


def test_unlog_before(handler):
    """
    Проверяем ситуацию, когда @unlog стоит до логирующего декоратора.
    """
    @unlog
    @flog(message='base text', level=100)
    def function():
        pass
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_unlog_after(handler):
    """
    Когда @unlog после логирующего декоратора.
    """
    @flog(message='base text', level=100)
    @unlog
    def function():
        pass
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_unlog_multiple(handler):
    """
    Когда логирующие декораторы по нескольку штук с обеих сторон от @unlog.
    """
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @unlog
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    def function():
        return True

    function()
    time.sleep(0.0001)

    assert len(handler.all) == 0

def test_working():
    """
    Проверяем, что декоратор не ломает поведение функции.
    """
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @unlog
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    def function():
        return True

    assert function() == True

def test_double_forbidden(handler):
    """
    Проверяем, что двойное наложение декоратора не ломает его работу.
    """
    @unlog
    @unlog
    @flog(message='base text', level=100)
    def function():
        pass
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_unlog_class(handler):
    """
    Пробуем запретить логирование в целом классе.
    Проверяем, что это работает.
    """
    config.set(pool_size=0)

    @unlog
    class Lol:
        @flog
        def kek(self, a, b):
            return a + b

    assert Lol().kek(2, 3) == 5
    assert handler.last is None

def test_incorrect_using_of_unlog():
    """
    Проверяем, что декоратор @unlog ругается, если передать туда что-то не то.
    """
    with pytest.raises(IncorrectUseOfTheDecoratorError):
        unlog('kek')
