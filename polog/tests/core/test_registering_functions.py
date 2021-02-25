import pytest
from polog.core.registering_functions import RegisteringFunctions
from polog import flog


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
    function = flog()(function)
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

def test_remove():
    """
    Проверяем, что функцию можно удалить из реестра задекорированных.
    """
    def function():
        pass
    register = RegisteringFunctions()
    decorated = flog()(function)
    assert register.is_decorator(decorated) == True
    register.remove(decorated)
    assert register.is_decorator(decorated) == False
    decorated = flog()(function)
    assert register.is_decorator(decorated) == True
    register.remove(decorated)

def test_forbid():
    """
    Проверяем, что после запрета на декорирование функции, @flog начинает возвращать оригинал.
    """
    def function():
        pass
    register = RegisteringFunctions()
    register.forbid(function)
    decorated = flog()(function)
    assert decorated is function
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
    assert id(function) in register.all_decorated_functions

def test_get_function_or_wrapper_forbidden():
    """
    Проверяем, что для функций, декорирование которых запрещено, возвращается оригинал.
    """
    def function():
        pass
    def wrapper():
        pass
    register = RegisteringFunctions()
    register.forbid(function)
    returned = register.get_function_or_wrapper(function, function, wrapper, False)
    assert returned is function

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
    function = flog()(abcde)
    assert register.is_decorator(function) == True
    function_id = id(function)
    del function
    del abcde
    assert function_id not in register.all_decorated_functions
