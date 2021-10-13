import pytest

from polog.core.utils.signature_matcher import SignatureMatcher


def test_is_handler_true(handler):
    """
    Проверка того, что обработчик с правильной сигнатурой распознается как обработчик.
    """
    assert SignatureMatcher.is_handler(handler) == True

def test_wrong_handlers():
    """
    Проверяем, что функции неправильных форматов не будут распознаны как обработчики.
    """
    def function_1():
        pass
    def function_2(**kwargs):
        pass
    def function_3(*args, **kwargs):
        pass
    def function_4(a, b):
        pass
    def function_5(a, b, c):
        pass
    assert SignatureMatcher.is_handler(function_1) == False
    assert SignatureMatcher.is_handler(function_2) == False
    assert SignatureMatcher.is_handler(function_3) == False
    assert SignatureMatcher.is_handler(function_4) == False
    assert SignatureMatcher.is_handler(function_5) == False

def test_wrong_object():
    """
    Пробуем скормить не вызываемый объект. Он не должен распознаваться как обработчик, при этом по умолчанию должно подниматься исключение.
    """
    with pytest.raises(ValueError):
        SignatureMatcher.is_handler('lol')

def test_wrong_object_not_raise():
    """
    Пробуем скормить не вызываемый объект с флагом raise_exception=False. Должно вернуться False.
    """
    assert SignatureMatcher.is_handler('lol', raise_exception=False) == False

def test_not_function():
    """
    Проверка, что вызываемый объект, не являющийся функцией, но имеющий нужную сигнатуру метода .__call__(), будет распознан как обработчик.
    """
    class PseudoFunction:
        def __call__(self, log):
            pass
    assert SignatureMatcher.is_handler(PseudoFunction()) == True

def test_random_functions():
    """
    Проверяем, что слепки сигнатур функций отрабатывают корректно.
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
    def function_7(a, b, c=False):
        pass
    def function_8(a, b, c=False, *d):
        pass
    def function_9(a, b, c=False, *d, **e):
        pass
    def function_10(a, b, c=False, c2=False, *d, **e):
        pass
    def function_11(a, b, b2, c=False, c2=False, *d, **e):
        pass
    def function_12(c=False, c2=False):
        pass
    assert SignatureMatcher().match(function_1) == True
    assert SignatureMatcher('.').match(function_2) == True
    assert SignatureMatcher('**').match(function_3) == True
    assert SignatureMatcher('*', '**').match(function_4) == True
    assert SignatureMatcher('.', '.').match(function_5) == True
    assert SignatureMatcher('.', '.', '.').match(function_6) == True
    assert SignatureMatcher('.', '.', 'c').match(function_7) == True
    assert SignatureMatcher('.', '.', 'c', '*').match(function_8) == True
    assert SignatureMatcher('.', '.', 'c', '*', '**').match(function_9) == True
    assert SignatureMatcher('.', '.', 'c', 'c2', '*', '**').match(function_10) == True
    assert SignatureMatcher('.', '.', '.', 'c', 'c2', '*', '**').match(function_11) == True
    assert SignatureMatcher('c', 'c2').match(function_12) == True

def test_random_wrong_functions():
    """
    Проверяем, что слепки сигнатур функций с неподходящими функциями не матчатся.
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
    def function_7(a, b, c=False):
        pass
    def function_8(a, b, c=False, *d):
        pass
    def function_9(a, b, c=False, *d, **e):
        pass
    def function_10(a, b, c=False, c2=False, *d, **e):
        pass
    def function_11(a, b, b2, c=False, c2=False, *d, **e):
        pass
    def function_12(c=False, c2=False):
        pass
    assert SignatureMatcher('.').match(function_1) == False
    assert SignatureMatcher('c').match(function_2) == False
    assert SignatureMatcher('.', '**').match(function_3) == False
    assert SignatureMatcher('.', '**').match(function_4) == False
    assert SignatureMatcher('.', 'c').match(function_5) == False
    assert SignatureMatcher('.', '.').match(function_6) == False
    assert SignatureMatcher('.', '.').match(function_7) == False
    assert SignatureMatcher('.', '.', 'c').match(function_8) == False
    assert SignatureMatcher('.', 'c', '*', '**').match(function_9) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_10) == False
    assert SignatureMatcher('.', '.', 'c2', '*', '**').match(function_11) == False
    assert SignatureMatcher('c').match(function_12) == False
