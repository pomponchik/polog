import time

import pytest

from polog.handlers.abstract.base import BaseHandler
from polog import handle_log as log, json_vars


class ConcreteHandler(BaseHandler):
    def do(self, content):
        log(content)

    def get_content(self, log):
        return str(log)

class ErrorHandler(BaseHandler):
    def do(self, content):
        raise ValueError

    def get_content(self, log):
        return str(log)

def test_filter_false(handler):
    """
    Проверяем, что фильтр, который всегда возвращает False, блокирует запись лога.
    """
    def false_filter(log):
        return False
    concrete = ConcreteHandler(filter=false_filter)
    concrete(dict(lol='kek'))
    time.sleep(0.0001)
    assert handler.last is None

def test_filter_true(handler):
    """
    Проверяем, что фильтр, который всегда возвращает True, не блокирует запись лога.
    """
    def true_filter(log):
        return True
    concrete = ConcreteHandler(filter=true_filter)
    concrete(dict(message='kek'))
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_false_true(handler):
    """
    Проверяем, что настройка only_errors в положении False не блокирует запись логов.
    """
    concrete = ConcreteHandler(only_errors=False)
    concrete(dict(message='kek', success=True))
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_false_false(handler):
    """
    Проверяем, что настройка only_errors в положении False не блокирует запись логов.
    """
    concrete = ConcreteHandler(only_errors=False)
    concrete(dict(message='kek', success=False))
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_true_false(handler):
    """
    Проверяем, что настройка only_errors в положении True не блокирует запись логов о неуспешных операциях.
    """
    concrete = ConcreteHandler(only_errors=True)
    concrete(dict(message='kek', success=False))
    time.sleep(0.0001)
    assert handler.last is not None

def test_only_errors_true_true(handler):
    """
    Проверяем, что настройка only_errors в положении True блокирует запись логов об успешных операциях.
    """
    concrete = ConcreteHandler(only_errors=True)
    concrete(dict(message='kek', success=True))
    time.sleep(0.0001)
    assert handler.last is None

def test_alt(handler):
    """
    Проверяем, что функция alt запускается, когда в обработчике что-то пошло не так.
    """
    def alt(log_item):
        log('lol')
    concrete = ErrorHandler(alt=alt)
    concrete(dict(message='kek'))
    time.sleep(0.0001)
    assert handler.last['message'] == 'lol'

def test_wrong_perams():
    """
    Проверка, что при неправильном использовании обработчика поднимается исключение.
    """
    with pytest.raises(ValueError):
        concrete = ConcreteHandler(only_errors='kek')
