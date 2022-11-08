import gc

import pytest

from polog.core.stores.registering_functions import RegisteringFunctions
from polog import log


def function_for_forbidden_test():
    pass


def test_is_decorator():
    """
    Проверяем, что только что созданная функция не определяется как задекорированная, а она же после декорирования - определяется.
    """
    def function():
        pass
    register = RegisteringFunctions()
    assert register.is_decorator(function) == False
    function = log()(function)
    assert register.is_decorator(function) == True
    register.remove(function)

def test_get_original():
    """
    Проверяем, что, передавая задекорированную функцию, мы получаем ее оригинал.
    """
    def function():
        pass
    register = RegisteringFunctions()
    assert id(register.get_original(function)) == id(function)
    decorated_function = log()(function)
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

def test_remove():
    """
    Проверяем, что функцию можно удалить из реестра задекорированных.
    """
    def function():
        pass
    register = RegisteringFunctions()
    decorated = log()(function)
    assert register.is_decorator(decorated) == True
    register.remove(decorated)
    assert register.is_decorator(decorated) == False
    decorated = log()(function)
    assert register.is_decorator(decorated) == True
    register.remove(decorated)

def test_is_forbidden():
    """
    Проверяем, что функция с запретом на декорирование успешно распознается как таковая, и наоборот.

    Функция для теста вынесена в глобал, т.к. возникала коллизия.
    Другие тесты помечали как запрещенные другие функции, после чего GC очищал память и в нее же могла дислоцироваться новая функция, объявленная в рамках данного теста. Соответственно, id совпадал. В результате при некоторых запусках теста все было ок, а при некоторых - тест падал.
    """
    def function():
        pass
    register = RegisteringFunctions()
    assert register.is_forbidden(function_for_forbidden_test) == False
    register.forbid(function_for_forbidden_test)
    assert register.is_forbidden(function_for_forbidden_test) == True

def test_add():
    """
    Проверяем, что функция добавляется в реестр.
    """
    def function():
        pass

    register = RegisteringFunctions()
    register.add(function, function)

    assert function in register.all_decorated_functions

def test_get_function_or_wrapper_forbidden():
    """
    Проверяем, что для функций, декорирование которых запрещено, возвращается оригинал, обернутый в @unlog.
    """
    def function():
        pass
    def wrapper():
        pass

    container = []

    register = RegisteringFunctions()
    register.forbid(function)
    register.get_function_or_wrapper(function, function, wrapper, False, unlog_decorator=container.append)

    assert container[0] is function

def test_get_function_or_wrapper_not_forbidden():
    """
    Проверяем, что для функций, декорирование которых НЕ запрещено, возвращается обертка.
    """
    def function():
        pass
    def wrapper():
        pass
    register = RegisteringFunctions()
    returned = register.get_function_or_wrapper(function, function, wrapper, False)
    assert returned is wrapper

def test_finalize():
    """
    Проверяем, что после удаления функции, она удаляется и из регистрирующего класса при помощи коллбека.
    """
    def abcde():
        pass
    register = RegisteringFunctions()
    function = log()(abcde)
    assert register.is_decorator(function) == True
    function_id = id(function)
    del function
    del abcde
    assert function_id not in register.all_decorated_functions

def test_add_unlogged_finalizer():
    """
    Проверяем, что при уничтожении объектов задекорированных @unlog'ом функций, они стираются из реестра.
    Много раз пересоздаем функцию с одним и тем же именем - предыдущие ее версии, соответственно, имеют 0 ссылок и должны уничтожаться механизмом подсчета ссылок. Из реестра она должна исчезнуть.
    """
    gc.collect()
    number_of_attempts = 1000

    size_before = len(RegisteringFunctions.unlogged_functions)

    for _ in range(number_of_attempts):
        def function():
            pass
        RegisteringFunctions().add_unlogged(function, function)
        del function

    gc.collect()

    size_after = len(RegisteringFunctions.unlogged_functions)

    assert size_after - size_before == 0

def test_simple_add_finalizer():
    """
    Проверяем, что, при уничтожении функции, она удаляется из реестра.
    """
    gc.collect()
    number_of_attempts = 1000

    size_before = len(RegisteringFunctions.all_decorated_functions)

    for _ in range(number_of_attempts):
        def function():
            pass
        RegisteringFunctions().add(function, function)
        del function

    gc.collect()

    size_after = len(RegisteringFunctions.all_decorated_functions)

    assert size_after - size_before == 0
