import time

import pytest

from polog import flog, logging_is_forbidden


def test_before(handler):
    """
    Проверяем ситуацию, когда @logging_is_forbidden стоит до логирующего декоратора.
    """
    @logging_is_forbidden
    @flog(message='base text', level=100)
    def function():
        pass
    handler.clean()
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_after(handler):
    """
    Когда @logging_is_forbidden после логирующего декоратора.
    """
    @flog(message='base text', level=100)
    @logging_is_forbidden
    def function():
        pass
    handler.clean()
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0

def test_multiple(handler):
    """
    Когда логирующие декораторы по нескольку штук с обеих сторон от @logging_is_forbidden.
    """
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @logging_is_forbidden
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    def function():
        return True
    handler.clean()
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
    @logging_is_forbidden
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
    @logging_is_forbidden
    @logging_is_forbidden
    @flog(message='base text', level=100)
    def function():
        pass
    handler.clean()
    function()
    time.sleep(0.0001)
    assert len(handler.all) == 0
