import pytest
from polog.core.registering_functions import RegisteringFunctions
from polog import flog


def test_is_decorated():
    """
    Проверяем, что только что созданная функция не определяется как задекорированная, а она же после декорирования - определяется.
    """
    def function():
        pass
    register = RegisteringFunctions()
    assert register.is_decorated(function) == False
    function = flog()(function)
    assert register.is_decorated(function) == True
    register.remove(function)

def test_get_original():
    """
    Проверяем, что, передавая задекорированную функцию, мы получаем ее оригинал.
    """
    def function():
        pass
    register = RegisteringFunctions()
    assert id(register.get_original(function)) == id(function)
    decorated_function = flog()(function)
    assert id(register.get_original(decorated_function)) == id(function)
    register.remove(function)

def test_is_method_false():
    """
    Проверяем, что функции, помеченные как методы, определятся как методы, и наоборот.
    Это используется для разруливания приоритетов между @clog и @flog.
    """
    def function():
        pass
    register = RegisteringFunctions()
    register.add(function, function, is_method=False)
    assert register.is_method(function) == False
    register.remove(function)

def test_is_method_true():
    """
    Проверяем, что функции, помеченные как методы, определятся как методы, и наоборот.
    Это используется для разруливания приоритетов между @clog и @flog.
    """
    def function():
        pass
    register = RegisteringFunctions()
    register.add(function, function, is_method=True)
    assert register.is_method(function) == True
    register.remove(function)
