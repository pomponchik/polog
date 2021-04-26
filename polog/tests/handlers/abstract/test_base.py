import time
import pytest
from polog.handlers.abstract.base import BaseHandler
from polog import handle_log as log, json_vars


class ConcreteHandler(BaseHandler):
    def do(self, content):
        log(content)

    def get_content(self, args, **kwargs):
        return str({**kwargs})

class ErrorHandler(BaseHandler):
    def do(self, content):
        raise ValueError

    def get_content(self, args, **kwargs):
        return str({**kwargs})

def test_filter_false(handler):
    """
    Проверяем, что фильтр, который всегда возвращает False, блокирует запись лога.
    """
    handler.clean()
    def false_filter(args, **kwargs):
        return False
    concrete = ConcreteHandler(filter=false_filter)
    concrete((None, None), message='kek')
    time.sleep(0.0001)
    assert handler.last is None

def test_filter_true(handler):
    """
    Проверяем, что фильтр, который всегда возвращает True, не блокирует запись лога.
    """
    handler.clean()
    def true_filter(args, **kwargs):
        return True
    concrete = ConcreteHandler(filter=true_filter)
    concrete((None, None), message='kek')
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_false_true(handler):
    """
    Проверяем, что настройка only_errors в положении False не блокирует запись логов.
    """
    handler.clean()
    concrete = ConcreteHandler(only_errors=False)
    concrete((None, None), message='kek', success=True)
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_false_false(handler):
    """
    Проверяем, что настройка only_errors в положении False не блокирует запись логов.
    """
    handler.clean()
    concrete = ConcreteHandler(only_errors=False)
    concrete((None, None), message='kek', success=False)
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_true_false(handler):
    """
    Проверяем, что настройка only_errors в положении True не блокирует запись логов о неуспешных операциях.
    """
    handler.clean()
    concrete = ConcreteHandler(only_errors=True)
    concrete((None, None), message='kek', success=False)
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_true_true(handler):
    """
    Проверяем, что настройка only_errors в положении True блокирует запись логов об успешных операциях.
    """
    handler.clean()
    concrete = ConcreteHandler(only_errors=True)
    concrete((None, None), message='kek', success=True)
    time.sleep(0.0001)
    assert handler.last is None

def test_alt(handler):
    """
    Проверяем, что функция alt запускается, когда в обработчике что-то пошло не так.
    """
    handler.clean()
    def alt(args, **kwargs):
        log('lol')
    concrete = ErrorHandler(alt=alt)
    concrete((None, None), message='kek')
    time.sleep(0.0001)
    assert handler.last['message'] == 'lol'

def test_wrong_perams():
    """
    Проверка, что при неправильном использовании обработчика поднимается исключение.
    """
    with pytest.raises(ValueError):
        concrete = ConcreteHandler(only_errors='kek')
