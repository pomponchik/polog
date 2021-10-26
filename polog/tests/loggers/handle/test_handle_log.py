import time
import json

import pytest

from polog import handle_log as log, json_vars, field, config


def test_base(handler):
    """
    Проверка, что в базовом случае лог записывается.
    """
    handler.clean()
    log('lol')
    time.sleep(0.0001)
    assert handler.last is not None

def test_exception(handler):
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

def test_level(handler):
    """
    Проверка, что указанный уровень лога срабатывает.
    """
    handler.clean()
    log('lol', level=100)
    time.sleep(0.0001)
    assert handler.last['level'] == 100

def test_function(handler):
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

def test_raise(handler):
    """
    Проверка, что при неправильно поданном типе именованной переменной возникает исключение.
    """
    handler.clean()
    config.set(silent_internal_exceptions=False)
    with pytest.raises(ValueError):
        log('lol', function=1)

non_local = []

def test_vars_to_local_variables(handler):
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

def test_vars_from_exception(handler):
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
    assert json.loads(handler.all[0]['local_variables']) == json.loads(handler.all[1]['local_variables'])

def test_another_field(handler):
    """
    Проверяем, что регистрируются пользовательские поля.
    """
    handler.clean()
    def extractor(log_item):
        pass
    config.add_fields(lolkek=field(extractor))

    log('kek', lolkek='lol')
    time.sleep(0.0001)
    assert handler.last['lolkek'] == 'lol'

def test_unknown_field(handler):
    """
    Проверяем, что при попытке записать в поле, не зарегистрированное ранее через config, поднимется исключение.
    """
    config.set(silent_internal_exceptions=False)
    with pytest.raises(KeyError):
        log('kek', lolkekcheburek='lol')

def test_getattribute(handler):
    """
    log() должно быть возможно вызывать не только непосредственно, но и через методы, имена которых соответствуют зарегистрированным пользователем уровням логирования.
    """
    handler.clean()
    config.levels(lolkek=777)
    log.lolkek("kek, i'm a cheburek")
    time.sleep(0.0001)
    assert handler.last['level'] == 777
    assert handler.last['message'] == "kek, i'm a cheburek"

def test_multiple_args():
    """
    Проверяем, что поднимается исключение, если вызвать log() с более чем одним позиционным аргументом.
    """
    config.set(silent_internal_exceptions=False)
    with pytest.raises(ValueError):
        log('lol', 'kek')

def test_extract_function_data_wrong_function_object():
    """
    Скармливаем псевдо-функцию.
    Если информацию о модуле невозможно извлечь, ничего не должно произойти.
    Если у функции отсутствует атрибут __name__, который извлекается по умолчанию, все равно функция в словаре будет заменена строкой.
    """
    class PseudoFunction:
        def __call__(self):
            return 'kek'
        @property
        def __module__(self):
            pass
        @__module__.getter
        def __module__(self):
            raise AttributeError('kek')
    pseudo = PseudoFunction()
    data = {'function': pseudo}
    log._extract_function_data(data)
    assert isinstance(data['function'], str)
    assert 'module' not in data['function']

def test_filter_logs_by_level(handler):
    """
    Проверяем, что лог уровнем ниже установленного не записывается.
    """
    handler.clean()
    config.set(level=5)

    log('kek', level=1)
    time.sleep(0.0001)
    assert handler.last is None
