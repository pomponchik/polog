import pytest
from polog.core.utils.is_handler import is_handler


def test_wrong_functions():
    """
    Проверяем, что функции неправильных форматов не будут распознаны как обработчики.
    """
    def function_1():
        pass
    def function_2(arg):
        pass
    def function_3(**kwargs):
        pass
    def function_4(*args, **kwargs):
        pass
    def function_5(a, b):
        pass
    def function_6(a, b, c):
        pass
    assert is_handler(function_1) == False
    assert is_handler(function_2) == False
    assert is_handler(function_3) == False
    assert is_handler(function_4) == False
    assert is_handler(function_5) == False
    assert is_handler(function_6) == False

def test_good_function():
    """
    Проверяем, что функция правильного формата распознается как обработчик.
    """
    def function(args, **kwargs):
        pass
    assert is_handler(function) == True

def test_wrong_object():
    """
    Пробуем скормить не вызываемый объект. Он не должен распознаваться как обработчик.
    """
    assert is_handler('lol') == False

def test_not_function():
    """
    Проверка, что вызываемый объект, не являющийся функцией, но имеющий нужную сигнатуру метода .__call__(), будет распознан как обработчик.
    """
    class PseudoFunction:
        def __call__(self, args, **kwargs):
            pass
    assert is_handler(PseudoFunction()) == True
