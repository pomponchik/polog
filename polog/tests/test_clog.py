import time
import pytest
from polog import clog, flog


@clog('important_method', message='base_message')
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
    handler.clean()
    ExampleOne().important_method()
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last['message'] == 'base_message'

def test_not_important_method(handler):
    """
    Проверка, что, если в декораторе класса были указаны нужные имена методов, то прочие методы логироваться не будут.
    """
    handler.clean()
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
    handler.clean()
    ExampleTwo().one_method()
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last['message'] == 'base_message_2'

def test_flog(handler):
    """
    Проверка, что при перекрестном логировании с flog все идет по плану.
    """
    handler.clean()
    ExampleTwo().two_method()
    time.sleep(0.0001)
    assert len(handler.all) == 1
    assert handler.last['level'] == 100
