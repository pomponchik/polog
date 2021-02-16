import pytest
from polog.core.utils.get_methods import get_methods


def test_methods_empty(empty_class):
    """
    Проверяем, что из "пустого" класса (который без методов) не извлекаются никакие методы.
    """
    methods = get_methods(empty_class)
    assert len(methods) == 0

def test_methods_one_method():
    """
    Проверяем, что из класса с одним методом извлекается только одно имя метода.
    """
    class TestClass:
        def test_method(self):
            pass
    methods = get_methods(TestClass)
    assert len(methods) == 1

def test_methods_not_danders():
    """
    Проверяем, что дандер-методы не учитываются.
    """
    class TestClass:
        def __method__(self):
            pass
    methods = get_methods(TestClass)
    assert len(methods) == 0
