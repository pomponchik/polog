import time

import pytest

from polog import clog, flog, config
from polog.errors import IncorrectUseOfTheDecoratorError


@clog(methods=('important_method',), message='base_message')
class ExampleOne:
    field = 'test'

    def important_method(self):
        pass

    def not_important_method(self):
        pass

@clog(message='base_message_2', level=1)
class ExampleTwo:
    def one_method(self):
        pass

    @flog(level=100)
    def two_method(self):
        pass

def test_important_method(handler):
    """
    Проверка, что указанные в декораторе класса по именам методы логируются.
    """
    config.set(level=1)
    ExampleOne().important_method()
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last['message'] == 'base_message'

def test_not_important_method(handler):
    """
    Проверка, что, если в декораторе класса были указаны нужные имена методов, то прочие методы логироваться не будут.
    """
    ExampleOne().not_important_method()
    time.sleep(0.0001)
    assert handler.last is None

def test_field():
    """
    Проверка, что декоратор класса не трогает обычные атрибуты.
    """
    assert ExampleOne.field == 'test'

def test_none_names(handler):
    """
    Проверка, что, если в декораторе класса не указаны имена методов, то логируются все.
    """
    config.set(level=1)
    ExampleTwo().one_method()
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last['message'] == 'base_message_2'

def test_flog(handler):
    """
    Проверка, что при перекрестном логировании с flog все идет по плану.
    """
    config.set(level=1)
    ExampleTwo().two_method()
    time.sleep(0.0001)
    assert len(handler.all) == 1
    assert handler.last['level'] == 100

def test_inherit_affect(handler):
    """
    Проверяем, что последний класс в иерархии наследования не аффектит работу своих предков при навешивании на него @clog.
    """
    config.set(level=1)
    class A:
        def a(self):
            pass
    @clog
    class B(A):
        def b(self):
            pass
    A().a()
    time.sleep(0.0001)
    assert handler.last is None

def test_inherit_affect_2(handler):
    """
    Еще одна проверка, что декорирование класса не аффектит предков.
    """
    config.set(level=1)
    @clog(message='message a')
    class A:
        def a(self):
            pass
    @clog(message='message b')
    class B(A):
        def b(self):
            pass
    A().a()
    time.sleep(0.0001)
    assert handler.last['message'] == 'message a'
    B().b()
    time.sleep(0.0001)
    assert handler.last['message'] == 'message b'
    B().a()
    time.sleep(0.0001)
    assert handler.last['message'] == 'message b'
    handler.clean()
    B().a()
    time.sleep(0.0001)
    assert len(handler.all) == 1
    assert 'b' not in dir(A)

def test_inherit_affect_3(handler):
    """
    Проверяем, что когда мы указываем в некоем классе список методов для логирования, унаследованные от залогированного класса методы, не перечисленные в данном списке, логироваться не будут.
    """
    config.set(level=1)
    @clog(message='message a')
    class A:
        def a(self):
            pass
    @clog(methods=('b',), message='message b')
    class B(A):
        def b(self):
            pass
    B().a()
    time.sleep(0.0001)
    assert handler.last is None
    A().a()
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last['message'] == 'message a'

def test_get_logging_methods_empty(empty_class):
    """
    Проверяем, что из "пустого" класса (который без методов) не извлекаются никакие методы.
    """
    methods = clog.get_logging_methods(empty_class)
    assert len(methods) == 0

def test_get_logging_methods_one_method():
    """
    Проверяем, что из класса с одним методом извлекается только одно имя метода.
    """
    class TestClass:
        def test_method(self):
            pass
    methods = clog.get_logging_methods(TestClass)
    assert len(methods) == 1

def test_get_logging_methods_not_danders():
    """
    Проверяем, что дандер-методы не учитываются.
    """
    class TestClass:
        def __method__(self):
            pass
    methods = clog.get_logging_methods(TestClass)
    assert len(methods) == 0

def test_wrong_using():
    """
    Проверяем, что если передать в декоратор не класс, поднимется исключение.
    """
    with pytest.raises(IncorrectUseOfTheDecoratorError):
        clog('kek')

def test_auto_flag_with_class(handler):
    """
    Проверяем, что флаг "auto" для логов, записанных через декоратор, проставляется в True.
    """
    @clog(message='kek')
    class A:
        def a(self):
            pass

    A().a()

    assert handler.last['auto'] == True
