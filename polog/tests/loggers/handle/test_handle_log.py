import time
import json
from datetime import datetime

import pytest

from polog import handle_log as log, json_vars, field, config
from polog.core.stores.settings.settings_store import SettingsStore


def test_base(handler):
    """
    Проверка, что в базовом случае лог записывается.
    """
    log('lol')
    time.sleep(0.0001)
    assert handler.last is not None

def test_exception(handler):
    """
    Проверка, что из исключения извлекается вся нужная инфа.
    """
    config.set(pool_size=0)

    try:
        raise ValueError('kek')
    except ValueError as e:
        log('lol', exception=e)

    assert handler.last is not None
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kek'

def test_level(handler):
    """
    Проверка, что указанный уровень лога срабатывает.
    """
    log('lol', level=100)
    time.sleep(0.0001)
    assert handler.last['level'] == 100

def test_function(handler):
    """
    Проверка, что из поданной функции автоматически извлекается имя функции и имя модуля.
    """
    def function():
        pass
    log('lol', function=function)
    time.sleep(0.0001)
    assert handler.last['function'] == function.__name__
    assert handler.last['module'] == function.__module__

def test_raise(handler):
    """
    Проверка, что при неправильно поданном типе именованной переменной возникает исключение.
    """
    config.set(silent_internal_exceptions=False)
    with pytest.raises(ValueError):
        log('lol', function=1)

non_local = []

def test_vars_to_local_variables(handler):
    """
    Проверяем, что переданные вручную локальные переменные попадают в лог.
    """
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
    def extractor(log_item):
        pass
    config.add_fields(lolkek=field(extractor))

    log('kek', lolkek='lol')
    time.sleep(0.0001)
    assert handler.last['lolkek'] == 'lol'

def test_getattribute(handler):
    """
    log() должно быть возможно вызывать не только непосредственно, но и через методы, имена которых соответствуют зарегистрированным пользователем уровням логирования.
    """
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
    config.set(level=5)

    log('kek', level=1)
    time.sleep(0.0001)
    assert handler.last is None

def test_set_value_to_not_specified_field_by_default(handler):
    """
    Пробуем скормить ручному логгеру поле с неизвестным ранее названием.
    Ожидаемое поведение по умолчанию (то есть с настройкой unknown_fields_in_handle_logs=True): значение должно напрямую оказаться в логе.
    """
    config.set(pool_size=0, unknown_fields_in_handle_logs=True, level=0)

    assert not config.get_all_fields('kekopekokek')

    log('kek', kekopekokek='kek')
    assert handler.last['kekopekokek'] == 'kek'

    log('kek', kekopekokek=5)
    assert handler.last['kekopekokek'] == 5

def test_set_value_to_not_specified_field_false(handler):
    """
    Пробуем скормить ручному логгеру поле с неизвестным ранее названием.
    Ожидаемое модифицированное поведение (то есть с настройкой unknown_fields_in_handle_logs=False): должно подняться исключение.
    """
    config.set(pool_size=0, unknown_fields_in_handle_logs=False)

    assert not config.get_all_fields('kekopekokek')

    with pytest.raises(KeyError):
        log('kek', kekopekokek='kek')

def test_setting_and_not_setting_of_service_name_when_handle_logging(handler):
    """
    Наличие ключа "service_name" в логе зависит от значения соответствующей настройки. При None ключ должен отсутствовать.
    Проверяем, что это так.
    """
    config.set(pool_size=0, service_name=None)

    log('lol')

    assert 'service_name' not in handler.last

    handler.clean()

    log('lol', exception=ValueError())

    assert 'service_name' not in handler.last

    handler.clean()
    config.set(service_name='base')

    log('kek')

    assert handler.last['service_name'] == 'base'

    handler.clean()

    log('kek', exception=ValueError())

    assert handler.last['service_name'] == 'base'

def test_auto_flag_in_handle_logging(handler):
    """
    Проверяем, что флаг "auto" для логов, записанных вручную, проставляется в False.
    """
    log('kek')

    assert handler.last['auto'] == False

def test_handle_logger_wrong_values():
    """
    Для ряда полей существуют специальные проверки, не позволяющие записать туда не подходящие по формату значения.
    Здесь мы пробуем записать неправильные значения и должны каждый раз ловить исключения.
    """
    with pytest.raises(ValueError):
        log('kek', function=1)
    with pytest.raises(ValueError):
        log('kek', module=1)
    with pytest.raises(ValueError):
        log('kek', module=lambda x: 'lol')
    with pytest.raises(ValueError):
        log(message=123)
    with pytest.raises(ValueError):
        log('kek', level=0.1)
    with pytest.raises(ValueError):
        log('kek', level=1.0)
    with pytest.raises(ValueError):
        log('kek', level=[])
    with pytest.raises(ValueError):
        log('kek', local_variables=[])
    with pytest.raises(ValueError):
        log('kek', success=5)
    with pytest.raises(ValueError):
        log('kek', success='yes')
    with pytest.raises(ValueError):
        log('kek', vars=3)
    with pytest.raises(ValueError):
        log('kek', class_=3)
    with pytest.raises(ValueError):
        log('kek', class_=lambda x: 'lol')

def test_level_name_converting_to_int_handle(handler):
    """
    Проверяем, что имя уровня логирования конвертится в число.
    """
    config.levels(kek=5)

    log('kek', level='kek')

    assert handler.last['level'] == 5

def test_converting_function_object_to_name(handler):
    """
    Проверяем, что если передать в качестве аргумента "function" в функцию log() объект функции, будет автоматически извлечено имя функции и модуль.
    """
    config.set(pool_size=0)

    def function_kek():
        pass

    log('kek', function=function_kek)

    assert handler.last['function'] == 'function_kek'
    assert handler.last['module'] == 'polog.tests.loggers.handle.test_handle_log'

def test_converting_exception_object_to_name(handler):
    """
    Проверяем, что при передаче объекта исключения извлекаются еще несколько полей.
    """
    config.set(pool_size=0, default_error_level=77)

    message = 'lolkek'
    log('kek', exception=ValueError(message))

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == message
    assert handler.last['success'] == False
    assert json.loads(handler.last['traceback']) == []
    assert handler.last['level'] == 77

def test_converting_exception_object_as_e_to_name(handler):
    """
    Проверяем, что при передаче объекта исключения извлекаются еще несколько полей.
    """
    config.set(pool_size=0, default_level=5, default_error_level=77)

    message = 'lolkek'
    log('kek', e=ValueError(message))

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == message
    assert handler.last['success'] == False
    assert json.loads(handler.last['traceback']) == []
    assert handler.last['level'] == 77

def test_extracting_local_variables_error_handle_logging(handler):
    """
    Проверяем, что локальные переменные при передаче исключения извлекаются автоматически в json.
    """
    a = 5
    b = 6

    try:
        raise ValueError('kek')
    except Exception as e:
        log('kek', exception=e)

    vars = json.loads(handler.last['local_variables'])['kwargs']

    assert vars['a'] == {"value": 5, "type": "int"}
    assert vars['b'] == {"value": 6, "type": "int"}
    assert vars['handler'] == {"value": str(handler), "type": type(handler).__name__}
    assert vars['e'] == {'value': 'kek', 'type': 'ValueError'}

def test_intersection_exception_and_e():
    """
    Пробуем одновременно задать конкурирующие параметры лога "e" и "exception".
    При значении настройки "silent_internal_exceptions", равном False, должно подняться исключение.
    """
    config.set(silent_internal_exceptions=False)

    with pytest.raises(ValueError):
        try:
            raise ValueError('kek')
        except Exception as e:
            log('kek', e=e, exception=KeyError('kek'))

def test_intersection_exception_and_e_silent(handler):
    """
    Пробуем одновременно задать конкурирующие параметры лога "e" и "exception".
    При значении настройки "silent_internal_exceptions", равном True, исключение подниматься не должно, запишется первое из переданных значений.
    """
    config.set(silent_internal_exceptions=True)

    try:
        raise ValueError('value')
    except Exception as e:
        log('kek', e=e, exception=KeyError('key'))

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'value'
    assert handler.last['success'] == False

def test_all_requirement_fields_are_of_expected_classes_with_handle_logging(handler):
    """
    Проверяем, что в самой базовой ситуации (когда при ручном логировании передается только сообщение) набор полей лога и классы данных в нем соответствуют ожидаемым.
    """
    config.set(pool_size=0, service_name='base')

    number_of_tries = 10000

    fields = {
        'time': datetime,
        'message': str,
        'level': int,
        'auto': bool,
        'service_name': str,
    }

    for index in range(number_of_tries):
        log('kek')
        for field_name, expected_class in fields.items():
            assert isinstance(handler.last[field_name], expected_class)
        handler.clean()

def test_normal_handle_log_from_decorator_does_not_contain_fields(handler):
    """
    Лог об успешной операции не должен содержать некоторые поля. Проверяем, что их действительно нет.
    """
    config.set(pool_size=0, service_name='base')

    number_of_tries = 10000

    fields = [
        'exception_type',
        'exception_message',
        'traceback',
        'local_variables',
        'function',
        'module'
        'input_variables',
        'local_variables',
        'result',
        'time_of_work',
        'class',
    ]

    for index in range(number_of_tries):
        log('kek')
        for field_name in fields:
            assert field_name not in handler.last
        handler.clean()

def test_extract_class_name_when_handle_logging(handler, empty_class):
    """
    Проверяем, что если передать объект класса, автоматом извлечется его имя.
    """
    config.set(pool_size=0)

    log('kek', class_=empty_class)

    assert handler.last['class'] == empty_class.__name__

def test_class_name_when_handle_logging(handler):
    """
    Проверяем, что если передать имя класса, оно прямиком попадет в лог.
    """
    config.set(pool_size=0)

    log('kek', class_='kek')

    assert handler.last['class'] == 'kek'

def test_handle_log_default_level(handler):
    """
    Проверяем, что по умолчанию для успешных событий берется дефолтный уровень из настроек.
    """
    config.set(pool_size=0, default_level=5)

    log('lol')
    assert handler.last['level'] == 5

    config.set(default_level=7)
    log('kek')
    assert handler.last['level'] == 7

def test_handle_log_not_default_level(handler):
    """
    Проверяем, что если клиент задал событию уровень, то используется именно он, а не взятый по дефолту из настроек.
    """
    config.set(pool_size=0, default_level=5)

    log('lol', level=7)
    assert handler.last['level'] == 7
