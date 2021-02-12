import time
import json
import pytest
from polog import log, config, json_vars
from polog.handlers.memory.saver import memory_saver


handler = memory_saver()
config.add_handlers(handler)


def test_base():
    """
    Проверка, что в базовом случае лог записывается.
    """
    handler.clean()
    log('lol')
    time.sleep(0.0001)
    assert handler.last is not None

def test_exception():
    """
    Проверка, что из исключения извлекается вся нужная инфа.
    """
    handler.clean()
    try:
        raise ValueError('kek')
    except ValueError as e:
        log('lol', exception=e)
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kek'

def test_level():
    """
    Проверка, что указанный уровень лога срабатывает.
    """
    handler.clean()
    log('lol', level=100)
    time.sleep(0.0001)
    assert handler.last['level'] == 100

def test_function():
    """
    Проверка, что из поданной функции автоматически извлекается имя функции и имя модуля.
    """
    def function():
        pass
    handler.clean()
    log('lol', function=function)
    time.sleep(0.0001)
    assert handler.last['function'] == function.__name__
    assert handler.last['module'] == function.__module__

def test_raise():
    """
    Проверка, что при неправильно поданном типе именованной переменной возникает исключение.
    """
    handler.clean()
    try:
        log('lol', function=1)
        assert False
    except ValueError:
        pass

non_local = []

def test_vars_to_local_variables():
    """
    Проверяем, что переданные вручную локальные переменные попадают в лог.
    """
    handler.clean()
    a = 1
    b = 2
    c = "3"
    log('lol', vars=json_vars(**locals()))
    time.sleep(0.0001)
    non_local.append(handler.last['local_variables'])
    non_local.append(json_vars(**locals()))
    assert non_local[0] == non_local[1]

def test_vars_from_exception():
    """
    Проверяем, что при исключении автоматически извлекаются те же данные о локальных переменных, что можно извлечь вручную.
    """
    handler.clean()
    a = 1
    b = 2
    c = "3"
    try:
        d = 3 / 0
    except ZeroDivisionError as e:
        k = e
        log('kek', exception=e)
    e = k
    time.sleep(0.0001)
    log('kek', vars=json_vars(**locals()))
    time.sleep(0.0001)
    assert json.loads(handler.all[0]['local_variables']) == json.loads(handler.all[1]['local_variables'])['kwargs']
