import sys
import time
import json
import asyncio
import traceback
from datetime import datetime

import pytest

from polog import log, config
from polog.core.utils.is_json import is_json
from polog.errors import IncorrectUseOfTheContextManagerError, IncorrectUseLoggerError
from polog.unlog import unlog
from polog.core.utils.exception_escaping import exception_escaping


def test_base_use(handler):
    """
    Проверка, что в базовом варианте использования (в виде обычной функции, без доп аргументов кроме сообщения лога) все работает.
    """
    log('kek')

    time.sleep(0.0001)

    assert handler.last['message'] == 'kek'

def test_base_use_dotlevel(handler):
    """
    Проверка, что в базовом варианте использования (в виде обычной функции, без доп аргументов, кроме сообщения лога), но с уровнем логирования, указанным через точку, все работает.
    """
    config.set(level=1)
    config.levels(test_base_use_dotlevel=44)
    log.test_base_use_dotlevel('kek')
    time.sleep(0.0001)
    assert handler.last['message'] == 'kek'
    assert handler.last['level'] == 44

def test_base_use_exception(handler):
    """
    Проверка, что данные из исключения извлекаются.
    """
    log('kek', e=ValueError('kek'))
    time.sleep(0.0001)
    assert handler.last['message'] == 'kek'
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kek'

def test_function_decorator_without_breacks(handler):
    """
    Проверка, что декоратор функций без скобок работает.
    """
    config.set(level=1)
    @log
    def function(a, b):
        return a + b
    assert function(1, 43) == 44
    time.sleep(0.001)
    assert handler.last is not None

def test_function_decorator_with_breacks(handler):
    """
    Проверка, что декоратор функций со скобками (но без доп аргументов в скобках) работает.
    """
    config.set(level=1)
    @log()
    def function(a, b):
        return a + b
    assert function(1, 33) == 34
    time.sleep(0.0001)
    assert handler.last is not None

def test_function_decorator_with_breacks_and_message(handler):
    """
    Проверка, что декоратор функций со скобками и с сообщением в скобках работает.
    """
    config.set(level=1)
    @log(message='kekokekokekokek')
    def function(a, b):
        return a + b
    assert function(1, 23) == 24
    time.sleep(0.0001)
    assert handler.last is not None
    assert handler.last['message'] == 'kekokekokekokek'

def test_function_decorator_with_breacks_and_message_and_dotlevel(handler):
    """
    Проверка, что декоратор функций со скобками и с сообщением в скобках, а также с уровнем логирования через точку, работает.
    """
    config.set(level=1)
    config.levels(test_function_decorator_with_breacks_and_message_and_dotlevel=42)

    @log.test_function_decorator_with_breacks_and_message_and_dotlevel(message='kek')
    def function(a, b):
        return a + b

    assert function(1, 13) == 14
    time.sleep(0.0001)

    assert handler.last is not None
    assert handler.last['message'] == 'kek'
    assert handler.last['level'] == 42

def test_function_decorator_with_breacks_and_message_and_dotlevel_async(handler):
    """
    Проверка, что декоратор функций со скобками и с сообщением в скобках, а также с уровнем логирования через точку, работает.
    """
    config.set(level=1)
    config.levels(test_function_decorator_with_breacks_and_message_and_dotlevel=42)

    @log.test_function_decorator_with_breacks_and_message_and_dotlevel(message='kek')
    async def function(a, b):
        return a + b

    assert asyncio.run(function(1, 13)) == 14
    time.sleep(0.0001)

    assert handler.last is not None
    assert handler.last['message'] == 'kek'
    assert handler.last['level'] == 42

def test_function_decorator_without_breacks_and_message_and_dotlevel(handler):
    """
    Проверка, что декоратор функций без скобок, но с уровнем логирования через точку, работает.
    """
    config.set(level=1)
    config.levels(test_function_decorator_without_breacks_and_message_and_dotlevel=43)

    @log.test_function_decorator_without_breacks_and_message_and_dotlevel
    def function(a, b):
        return a + b

    assert function(1, 3) == 4
    time.sleep(0.0001)

    assert handler.last is not None
    assert handler.last['level'] == 43

def test_function_decorator_without_breacks_and_message_and_dotlevel_async(handler):
    """
    Проверка, что декоратор функций без скобок, но с уровнем логирования через точку, работает.
    """
    config.set(level=1)
    config.levels(test_function_decorator_without_breacks_and_message_and_dotlevel=43)

    @log.test_function_decorator_without_breacks_and_message_and_dotlevel
    async def function(a, b):
        return a + b

    assert asyncio.run(function(1, 3)) == 4
    time.sleep(0.0001)

    assert handler.last is not None
    assert handler.last['level'] == 43

def test_define_level_name_after_using_in_the_decorator(handler):
    """
    Проверяем, что можно задать имя уровню уже после использования в декораторе.
    """
    config.set(level=0, pool_size=0)

    @log.test_define_level_name_after_using_in_the_decorator
    def function(a, b):
        return a + b

    config.levels(test_define_level_name_after_using_in_the_decorator=456)

    assert function(1, 3) == 4
    assert handler.last is not None
    assert handler.last['level'] == 456

def test_message(handler):
    """
    Проверка, что редактирование сообщений лога работает.
    """
    config.set(level=1)

    @log
    def function(a, b):
        log.message('kek', level=5)
        return a + b

    assert function(1, 2) == 3
    time.sleep(0.0001)

    assert handler.last is not None
    assert handler.last['message'] == 'kek'
    assert handler.last['level'] == 5

def test_message_async(handler):
    """
    Проверка, что редактирование сообщений лога работает для корутинных функций.
    """
    config.set(level=1)

    @log
    async def function(a, b):
        log.message('kek', level=5)
        return a + b

    assert asyncio.run(function(1, 2)) == 3
    time.sleep(0.0001)

    assert handler.last is not None
    assert handler.last['message'] == 'kek'
    assert handler.last['level'] == 5

def test_simple_log_decorator_with_positional_message(handler):
    """
    Пробуем передать сообщение в декоратор в качестве позиционного аргумента.
    """
    config.set(level=1, pool_size=0)

    @log('kek')
    def function():
        return 3

    assert function() == 3

    assert handler.last['message'] == 'kek'

def test_simple_log_decorator_with_positional_message_and_dotlevel(handler):
    """
    Пробуем передать сообщение в декоратор в качестве позиционного аргумента, с названием уровня через точку.
    """
    config.set(level=1, pool_size=0)

    config.levels(kek=5)

    @log.kek('kek')
    def function():
        return 3

    assert function() == 3

    assert handler.last['message'] == 'kek'

def test_time_is_before_of_calling_function_in_decorator(handler):
    """
    Проверяем, что в режиме декоратора время операции записывается ДО операции, а не после.
    """
    @log
    def function():
        time.sleep(0.001)

    before_stamp = datetime.now()
    function()
    after_stamp = datetime.now()

    delta = after_stamp - before_stamp
    half_delta = delta / 2
    half_plus_before_stamp = before_stamp + half_delta

    assert handler.last['time'] < half_plus_before_stamp

def test_time_is_before_of_working_in_context_manager(handler):
    """
    Проверяем, что в режиме контекстного менеджера время операции записывается ДО операции, а не после.
    """
    before_stamp = datetime.now()
    with log('kek'):
        time.sleep(0.001)
    after_stamp = datetime.now()

    delta = after_stamp - before_stamp
    half_delta = delta / 2
    half_plus_before_stamp = before_stamp + half_delta

    assert handler.last['time'] < half_plus_before_stamp

def test_context_manager_exception_message(handler):
    """
    Проверяем, что поле 'exception_message' внутри лога при использовании контекстного менеджера заполняется корректно.
    """
    config.set(level=1, pool_size=0, suppress_by_default=True)

    with log('kek'):
        raise ValueError
    assert handler.last['exception_message'] == ''

    with log('kek'):
        raise ValueError('cheburek')
    assert handler.last['exception_message'] == 'cheburek'

    with log('kek'):
        pass
    assert 'exception_message' not in handler.last

    config.set(suppress_by_default=False)

    with pytest.raises(ValueError):
        with log('kek'):
            raise ValueError
    assert handler.last['exception_message'] == ''

    with pytest.raises(ValueError):
        with log('kek'):
            raise ValueError('cheburek')
    assert handler.last['exception_message'] == 'cheburek'

    with log('kek'):
        pass
    assert 'exception_message' not in handler.last

def test_simple_context_manager_write_log_and_reraise_exception(handler):
    """
    Проверяем, что при использовании log() в качестве контекстного менеджера при значении настройки suppress_by_default, равном False:
    1. Исключение не подавляется.
    2. Содержимое всех полей соответствует ожиданиям.
    """
    default_error_level = 45
    config.set(level=1, pool_size=0, suppress_by_default=False, default_level=3, default_error_level=default_error_level)

    with pytest.raises(ValueError):
        with log('kek'):
            raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['message'] == 'kek'
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert handler.last['auto'] == False
    assert handler.last['level'] == default_error_level
    assert handler.last['success'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0

    assert is_json(handler.last['traceback'])

def test_simple_context_manager_write_log_and_suppress_exception_by_default(handler):
    """
    Проверяем, что при использовании log() в качестве контекстного менеджера при значении настройки suppress_by_default, равном True:
    1. Исключение подавляется.
    2. Содержимое всех полей соответствует ожиданиям.
    """
    default_error_level = 45
    config.set(level=1, pool_size=0, suppress_by_default=True, default_level=3, default_error_level=default_error_level)

    with log('kek'):
        raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['message'] == 'kek'
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert handler.last['auto'] == False
    assert handler.last['level'] == default_error_level
    assert handler.last['success'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0

    assert is_json(handler.last['traceback'])

def test_simple_using_of_context_manager(handler):
    """
    Пробуем использовать контекстный менеджер в самой простой ситуации, без исключений внутри.
    Проверяем, что итоговый набор полей лога совпадает с ожидаемым.
    """
    default_level = 3
    config.set(level=1, pool_size=0, default_level=default_level)

    with log('kek'):
        pass

    assert handler.last is not None

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['message'] == 'kek'
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

def test_using_of_context_manager_with_positional_argument_and_named_one(handler):
    """
    Тест аналогичен test_simple_using_of_context_manager, но в контекстный менеджер передается не только позиционный аргумент, но и именованный.
    """
    default_level = 3
    config.set(level=1, pool_size=0, default_level=default_level)

    with log('kek', lol='cheburek'):
        pass

    assert handler.last is not None

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['message'] == 'kek'
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert handler.last['lol'] == 'cheburek'

def test_add_named_field_to_context_manager(handler):
    """
    Пробуем добавить новое поле в лог внутри контекста.
    """
    default_level = 3
    config.set(level=1, pool_size=0, default_level=default_level)

    with log('kek', lol='cheburek') as context:
        context(pek='lol')

    assert handler.last is not None

    assert handler.last['message'] == 'kek'
    assert handler.last['pek'] == 'lol'
    assert handler.last['lol'] == 'cheburek'

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

def test_replace_message_in_context_manager(handler):
    """
    Пробуем заменить сообщение внутри контекстного менеджера.
    """
    default_level = 3
    config.set(level=1, pool_size=0, default_level=default_level)

    with log('kek', lol='cheburek') as context:
        context('lol')

    assert handler.last is not None

    assert handler.last['message'] == 'lol'
    assert handler.last['lol'] == 'cheburek'

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

def test_replace_message_in_context_manager_as_named_argument(handler):
    """
    Пробуем заменить сообщение внутри контекстного менеджера.
    """
    default_level = 3
    config.set(level=1, pool_size=0, default_level=default_level)

    with log('kek', lol='cheburek') as context:
        context(message='lol')

    assert handler.last is not None

    assert handler.last['message'] == 'lol'
    assert handler.last['lol'] == 'cheburek'

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

def test_replace_field_in_context_manager_as_named_argument(handler):
    """
    Пробуем заменить содержимое поля внутри контекстного менеджера.
    """
    default_level = 3
    config.set(level=1, pool_size=0, default_level=default_level)

    with log('kek', lol='cheburek') as context:
        context(lol='lol')

    assert handler.last is not None

    assert handler.last['message'] == 'kek'
    assert handler.last['lol'] == 'lol'

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

def test_multiple_rewriting_in_context_manager(handler):
    """
    Пробуем несколько раз отредактировать лог внутри контекстного менеджера.
    """
    default_level = 3
    config.set(level=1, pool_size=0, default_level=default_level)

    with log('kek', lol='cheburek') as context:
        context(lol='lol')
        context(pek='pekopek')
        context(mek='mekopek')
        context(zhek='zhekopek')

    assert handler.last is not None

    assert handler.last['message'] == 'kek'
    assert handler.last['lol'] == 'lol'
    assert handler.last['pek'] == 'pekopek'
    assert handler.last['mek'] == 'mekopek'
    assert handler.last['zhek'] == 'zhekopek'

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

def test_multiple_rewriting_in_context_manager_before_exception(handler):
    """
    Пробуем несколько раз отредактировать лог внутри контекстного менеджера перед тем, как поднять исключение.
    """
    default_level = 3
    default_error_level = 45
    config.set(level=1, pool_size=0, default_level=default_level, default_error_level=default_error_level, suppress_by_default=False)

    with pytest.raises(ValueError):
        with log('kek', lol='cheburek') as context:
            context(lol='lol')
            context(pek='pekopek')
            context(mek='mekopek')
            context(zhek='zhekopek')
            raise ValueError('kek')

    assert handler.last is not None

    assert handler.last['message'] == 'kek'
    assert handler.last['lol'] == 'lol'
    assert handler.last['pek'] == 'pekopek'
    assert handler.last['mek'] == 'mekopek'
    assert handler.last['zhek'] == 'zhekopek'

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kek'
    assert is_json(handler.last['traceback'])

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False

    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == False
    assert handler.last['level'] == default_error_level

def test_double_entering_to_context():
    """
    Пробуем повторно войти в контекстный менеджер, должно подняться исключение.
    """
    config.set(suppress_by_default=False)

    with pytest.raises(AttributeError):
        with log('lol') as context:
            with context('kek'):
                pass

def test_give_to_suppress_no_exception():
    """
    Пробуем передать в метод .suppress() не исключение.
    При значении настройки silent_internal_exceptions, равном True, должно подняться исключение, в противном случае - нет.
    """
    config.set(silent_internal_exceptions=False)

    with pytest.raises(ValueError):
        with log('kek').suppress('lol'):
            pass

    config.set(silent_internal_exceptions=True)

    with log('kek').suppress('lol'):
        pass

def test_give_to_suppress_no_exception_and_exception():
    """
    Пробуем передать в метод .suppress() не исключение и исключение.
    При значении настройки silent_internal_exceptions, равном True, должно подняться исключение, в противном случае - нет.
    Если silent_internal_exceptions == False, те аргументы, которые являются исключениями, таки должны зафиксироваться.
    """
    config.set(silent_internal_exceptions=False)

    with pytest.raises(ValueError):
        with log('kek').suppress('lol', ValueError):
            pass

    config.set(silent_internal_exceptions=True)

    with log('kek').suppress('lol', ValueError):
        raise ValueError

    with pytest.raises(KeyError):
        with log('kek').suppress('lol', ValueError):
            raise KeyError

def test_context_manager_simple_suppress_exception_with_default_false(handler):
    """
    Пробуем использовать метод .suppress() в определении контекста без дополнительных аргументов.
    Должно блокировать все исключения.
    """
    config.set(pool_size=0, suppress_by_default=False)

    with log('kek').suppress():
        raise ValueError

    assert handler.last is not None

    handler.clean()

    with log('kek').suppress():
        raise Exception

    assert handler.last is not None

def test_context_manager_simple_suppress_exception_with_default_true(handler):
    """
    Пробуем использовать метод .suppress() в определении контекста без дополнительных аргументов.
    Должно блокировать все исключения.
    """
    config.set(pool_size=0, suppress_by_default=True)

    with log('kek').suppress():
        raise ValueError

    assert handler.last is not None

    handler.clean()

    with log('kek').suppress():
        raise Exception

    assert handler.last is not None

def test_context_manager_suppress_same_class_exception_with_default_false(handler):
    """
    Пробуем использовать метод .suppress() по прямому назначению.
    Контекстный менеджер должен в этом случае блокировать переданные исключения и не блокировать не переданные.
    Значения дефолта при этом ни на что влиять не должны.
    """
    config.set(pool_size=0, suppress_by_default=False)

    with log('kek').suppress(ValueError):
        raise ValueError

    with pytest.raises(KeyError):
        with log('kek').suppress(ValueError):
            raise KeyError

def test_context_manager_suppress_same_class_multiple_exceptions_with_default_false(handler):
    """
    Тест аналогичен test_context_manager_suppress_same_class_exception_with_default_false, но на этот раз в .suppress() передаются несколько классов исключений.
    """
    config.set(pool_size=0, suppress_by_default=False)

    with log('kek').suppress(ValueError, KeyError):
        raise ValueError

    with log('kek').suppress(ValueError, KeyError):
        raise KeyError

    with pytest.raises(RuntimeError):
        with log('kek').suppress(ValueError, KeyError):
            raise RuntimeError

def test_context_manager_suppress_same_class_exception_with_default_true(handler):
    """
    Тест аналогичен test_context_manager_suppress_same_class_exception_with_default_false, но здесь меняется значение глобальной настройки 'suppress_by_default' на True. Это не должно ни на что влиять, результат должен остаться тем же, поскольку .suppress() локально полностью переопределяет настройки, указанные глобально.
    """
    config.set(pool_size=0, suppress_by_default=True)

    with log('kek').suppress(ValueError):
        raise ValueError

    with pytest.raises(KeyError):
        with log('kek').suppress(ValueError):
            raise KeyError

def test_context_manager_suppress_subclass_of_exception():
    """
    Проверяем, что настройка 'suppress_exception_subclasses' работает.
    При значении True, субклассы исключений переданных в .suppress() тоже должны подавляться. В значении False исключение подавляется только при если классы точно совпадают.
    """
    config.set(pool_size=0, suppress_exception_subclasses=True)

    class SubclassValueError(ValueError):
        pass

    with log('kek').suppress(ValueError):
        raise SubclassValueError('kek')

    config.set(suppress_exception_subclasses=False)

    with pytest.raises(SubclassValueError):
        with log('kek').suppress(ValueError):
            raise SubclassValueError('kek')

def test_context_manager_without_arguments_and_suppress_exception_subclasses_false(handler):
    """
    Если .suppress() используется без аргументов, любые исключения должны подавляться в любом случае (вне зависимости от значения настройки 'suppress_exception_subclasses').
    """
    config.set(pool_size=0, suppress_exception_subclasses=False)

    with log('kek').suppress():
        raise ValueError

    assert handler.last is not None

def test_minus_log_is_unlog():
    """
    Отрицание объекта log должно давать unlog.
    """
    assert -log is unlog

def test_context_manager_simple_call_with_silent_internal_exceptions_off(handler):
    """
    Проверяем, что при настройке 'silent_internal_exceptions', равной Falsе, неизвестные поля лога записываются через контекстный менеджер.
    """
    config.set(pool_size=0, silent_internal_exceptions=False)

    with log('kek', llelel=600, knijbn='lol'):
        pass

    assert handler.last is not None
    assert handler.last['llelel'] == 600
    assert handler.last['knijbn'] == 'lol'

def test_router_two_positional_arguments():
    """
    Нельзя передавать в log() два и более позиционных аргумента, можно строго один. Проверяем, что при попытке это сделать поднимается исключение.
    """
    with pytest.raises(IncorrectUseLoggerError):
        log('1', '2')

def test_router_incorrect_positional_argument():
    """
    В log() в качестве позиционного аргумента можно передать только строку. Проверяем, что в ином случае поднимется исключение.
    """
    with pytest.raises(IncorrectUseLoggerError):
        log(1)

def test_router_class_decorator_without_brackets(handler):
    """
    Пробуем навесить log как декоратор на класс, без скобок.
    """
    default_level = 555
    config.set(pool_size=0, default_level=default_level)

    @log
    class SomeClass:
        def method(self):
            pass

    SomeClass().method()

    assert handler.last is not None

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['success'] == True
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_level

    assert isinstance(handler.last['time_of_work'], float)

    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last
    assert 'message' not in handler.last

def test_router_method_decorator_without_brackets(handler):
    """
    Пробуем навесить log как декоратор на обычный метод класса, без скобок.
    """
    default_level = 555
    config.set(pool_size=0, default_level=default_level)

    class SomeClass:
        @log
        def method(self):
            pass

    SomeClass().method()

    assert handler.last is not None

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['module'] == 'polog.tests.loggers.test_router'
    assert handler.last['success'] == True
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_level

    assert isinstance(handler.last['time_of_work'], float)

    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last
    assert 'message' not in handler.last

def test_router_class_decorator_with_empty_brackets(handler):
    """
    Пробуем навесить log как декоратор на класс, с пустыми скобками.
    """
    default_level = 555
    config.set(pool_size=0, default_level=default_level)

    @log()
    class SomeClass:
        def method(self):
            pass

    SomeClass().method()

    assert handler.last is not None

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['success'] == True
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_level

    assert isinstance(handler.last['time_of_work'], float)

    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last
    assert 'message' not in handler.last

def test_router_method_decorator_with_empty_brackets(handler):
    """
    Пробуем навесить log как декоратор на обычный метод класса, с пустыми скобками.
    """
    default_level = 555
    config.set(pool_size=0, default_level=default_level)

    class SomeClass:
        @log()
        def method(self):
            pass

    SomeClass().method()

    assert handler.last is not None

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['module'] == 'polog.tests.loggers.test_router'
    assert handler.last['success'] == True
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_level

    assert isinstance(handler.last['time_of_work'], float)

    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last
    assert 'message' not in handler.last

def test_router_class_decorator_with_wrong_list_of_methods():
    """
    Пробуем вместо списка имен методов передать что-то другое. Должны подниматься исключения.
    """
    with pytest.raises(TypeError):
        @log(methods=1)
        class SomeClass:
            pass
    with pytest.raises(TypeError):
        @log(methods=[1, 2, 3])
        class SomeClass:
            pass

def test_router_class_decorator_with_list_of_methods(handler):
    """
    Пробуем передать в декоратор класса список имен методов, которые нужно залогировать.
    Проверяем, что методы с переданным набором имен логируются, а остальные нет.
    """
    default_level = 555
    config.set(pool_size=0, default_level=default_level)

    @log(methods=['important_method'])
    class SomeClass:
        def important_method(self):
            pass
        def not_important_method(self):
            pass

    SomeClass().not_important_method()

    assert handler.last is None

    SomeClass().important_method()

    assert handler.last is not None

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'important_method'
    assert handler.last['module'] == 'polog.tests.loggers.test_router'
    assert handler.last['success'] == True
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_level

    assert isinstance(handler.last['time_of_work'], float)

    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last
    assert 'message' not in handler.last

def test_router_class_decorator_with_level(handler):
    """
    Проверяем, что, если в декоратор класса передать уровень логирования, все будет работать.
    """
    default_level = 555
    real_level = 5
    config.set(pool_size=0, default_level=default_level)

    @log(level=real_level)
    class SomeClass:
        def method(self):
            pass

    SomeClass().method()

    assert handler.last is not None

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['module'] == 'polog.tests.loggers.test_router'
    assert handler.last['success'] == True
    assert handler.last['auto'] == True
    assert handler.last['level'] == real_level

    assert isinstance(handler.last['time_of_work'], float)

    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last
    assert 'message' not in handler.last

def test_router_class_decorator_with_positional_message(handler):
    """
    Пробуем в декоратор класса подать сообщение в виде первого неименованного аргумента.
    """
    default_level = 555
    config.set(pool_size=0, default_level=default_level)

    @log("kek")
    class SomeClass:
        def method(self):
            pass

    SomeClass().method()

    assert handler.last is not None

    assert handler.last['message'] == 'kek'

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['module'] == 'polog.tests.loggers.test_router'
    assert handler.last['success'] == True
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_level

    assert isinstance(handler.last['time_of_work'], float)

    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

def test_router_method_decorator_with_empty_brackets_when_exception(handler):
    """
    Пробуем навесить log как декоратор на обычный метод класса, с пустыми скобками.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level)

    class SomeClass:
        @log()
        def method(self):
            raise ValueError('kekokek')

    with pytest.raises(ValueError):
        SomeClass().method()

    assert handler.last is not None

    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['module'] == 'polog.tests.loggers.test_router'
    assert handler.last['success'] == False
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_error_level

    assert isinstance(handler.last['time_of_work'], float)

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kekokek'
    assert 'message' not in handler.last

def test_router_method_decorator_with_positional_message_when_exception(handler):
    """
    Пробуем навесить log как декоратор на обычный метод класса, передав туда в виде позиционного аргумента сообщение лога.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level)

    class SomeClass:
        @log('kek')
        def method(self):
            raise ValueError('kekokek')

    with pytest.raises(ValueError):
        SomeClass().method()

    assert handler.last is not None

    assert handler.last['message'] == 'kek'
    assert handler.last['class'] == 'SomeClass'
    assert handler.last['function'] == 'method'
    assert handler.last['module'] == 'polog.tests.loggers.test_router'
    assert handler.last['success'] == False
    assert handler.last['auto'] == True
    assert handler.last['level'] == default_error_level

    assert isinstance(handler.last['time_of_work'], float)

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kekokek'

def test_context_manager_without_brackets_and_attributes(handler):
    """
    Пробуем использовать log как контекстный менеджер без скобок.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level)

    with log:
        pass

    assert handler.last is not None

    assert 'message' not in handler.last
    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

def test_context_manager_without_brackets_and_attributes_with_context_addind(handler):
    """
    Пробуем при использовании log как контекстного менеджера без скобок отредактировать записываемый лог изнутри контекста.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level)

    with log as context:
        context('kek', some_variable='some text')

    assert handler.last is not None

    assert 'traceback' not in handler.last
    assert 'exception_type' not in handler.last
    assert 'exception_message' not in handler.last

    assert handler.last['message'] == 'kek'
    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == True
    assert handler.last['level'] == default_level

    assert handler.last['some_variable'] == 'some text'

def test_exception_in_context_manager_without_brackets_and_attributes(handler):
    """
    Пробуем использовать log как контекстный менеджер без скобок для исключения.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level, suppress_by_default=False)

    with pytest.raises(ValueError):
        with log:
            raise ValueError('kek')

    assert handler.last is not None

    assert 'message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == False
    assert handler.last['level'] == default_error_level

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kek'
    assert is_json(handler.last['traceback'])

def test_exception_in_context_manager_without_brackets_and_attributes_suppress_by_default_on(handler):
    """
    Пробуем использовать log как контекстный менеджер без скобок для ловли исключения.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level, suppress_by_default=True)

    with log:
        raise ValueError('kek')

    assert handler.last is not None

    assert 'message' not in handler.last

    assert isinstance(handler.last['time'], datetime)
    assert handler.last['auto'] == False
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['success'] == False
    assert handler.last['level'] == default_error_level

    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'kek'
    assert is_json(handler.last['traceback'])

def test_multiple_context_managers_without_brackets_and_attributes(handler):
    """
    Пробуем вложить друг в друга контекстные менеджеры. Проверяем, что они записываются в нужном порядке.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level, suppress_by_default=True)

    with log:
        with log:
            raise ValueError('kek')

    assert len(handler.all) == 2

    assert handler.all[0]['level'] == default_error_level
    assert handler.all[1]['level'] == default_level

def test_context_manager_without_brackets_with_dotlevel_defined_before(handler):
    """
    Проверяем, что указание имени уровня логирования через точку в контекстном менеджере без скобок - работает.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, default_level=default_level, default_error_level=default_error_level, suppress_by_default=True)
    config.levels(test_context_manager_without_brackets_with_dotlevel_defined_before=55)

    with log.test_context_manager_without_brackets_with_dotlevel_defined_before:
        pass

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['level'] == 55

def test_context_manager_without_brackets_with_empty_supppress_only(handler):
    """
    Проверяем, что метод .suppress() без скобок в контекстном менеджере - работает.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, suppress_by_default=False, default_level=default_level, default_error_level=default_error_level)

    with log.suppress():
        raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['success'] == False
    assert handler.last['auto'] == False

    assert isinstance(handler.last['time'], datetime)
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['level'] == default_error_level
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert is_json(handler.last['traceback'])

def test_context_manager_without_brackets_with_empty_supppress_and_one_another_arg(handler):
    """
    Проверяем, что метод .suppress() без скобок в контекстном менеджере - работает, если передать туда исключение.
    Мы пробуем туда передать исключение, которое отличается от того, которое мы хотим подавить - оно должно пройти сквозь контекстный менеджер.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, suppress_by_default=False, default_level=default_level, default_error_level=default_error_level)

    with pytest.raises(ValueError):
        with log.suppress(TypeError):
            raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['success'] == False
    assert handler.last['auto'] == False

    assert isinstance(handler.last['time'], datetime)
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['level'] == default_error_level
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert is_json(handler.last['traceback'])

def test_context_manager_without_brackets_with_empty_supppress_and_one_exactly_arg(handler):
    """
    Проверяем, что метод .suppress() без скобок в контекстном менеджере - работает, если передать туда исключение.
    Мы пробуем туда передать такое же исключение, как и то, которое мы хотим подавить - оно должно быть подавлено.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, suppress_by_default=False, default_level=default_level, default_error_level=default_error_level)

    with log.suppress(ValueError):
        raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['success'] == False
    assert handler.last['auto'] == False

    assert isinstance(handler.last['time'], datetime)
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['level'] == default_error_level
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert is_json(handler.last['traceback'])

def test_context_manager_without_brackets_with_exceptions_in_supppress_and_dotlevel(handler):
    """
    Проверяем, что метод .suppress() без скобок в контекстном менеджере - работает.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, suppress_by_default=False, default_level=default_level, default_error_level=default_error_level)

    config.levels(test_context_manager_without_brackets_with_exceptions_in_supppress_and_dotlevel=55)

    with log.test_context_manager_without_brackets_with_exceptions_in_supppress_and_dotlevel.suppress():
        raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['success'] == False
    assert handler.last['auto'] == False

    assert isinstance(handler.last['time'], datetime)
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['level'] == 55
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert is_json(handler.last['traceback'])

def test_context_manager_without_brackets_with_exceptions_in_supppress_and_one_another_arg_and_dotlevel(handler):
    """
    Проверяем, что метод .suppress() без скобок в контекстном менеджере - работает, если передать туда исключение, когда мы ловим другое.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, suppress_by_default=False, default_level=default_level, default_error_level=default_error_level)

    config.levels(test_context_manager_without_brackets_with_exceptions_in_supppress_and_one_another_arg_and_dotlevel=55)

    with pytest.raises(ValueError):
        with log.test_context_manager_without_brackets_with_exceptions_in_supppress_and_one_another_arg_and_dotlevel.suppress(TypeError):
            raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['success'] == False
    assert handler.last['auto'] == False

    assert isinstance(handler.last['time'], datetime)
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['level'] == 55
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert is_json(handler.last['traceback'])

def test_context_manager_without_brackets_with_exceptions_in_supppress_and_one_exactly_arg_and_dotlevel(handler):
    """
    Проверяем, что метод .suppress() без скобок в контекстном менеджере - работает, если передать туда исключение, когда мы ловим другое.
    """
    default_level = 555
    default_error_level = 777
    config.set(pool_size=0, suppress_by_default=False, default_level=default_level, default_error_level=default_error_level)

    config.levels(test_context_manager_without_brackets_with_exceptions_in_supppress_and_one_another_arg_and_dotlevel=55)

    with log.test_context_manager_without_brackets_with_exceptions_in_supppress_and_one_another_arg_and_dotlevel.suppress(ValueError):
        raise ValueError

    assert handler.last is not None
    assert len(handler.all) == 1

    assert handler.last['success'] == False
    assert handler.last['auto'] == False

    assert isinstance(handler.last['time'], datetime)
    assert 'time_of_work' in handler.last
    assert isinstance(handler.last['time_of_work'], float)
    assert handler.last['time_of_work'] > 0
    assert handler.last['level'] == 55
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == ''
    assert is_json(handler.last['traceback'])

def test_local_vars_if_no_exception_escaping(handler):
    """
    Проверяем, что, если при ручном логировании передать экземпляр исключения, не находясь при этом в блоке except, то поле 'local_variables' не заполняется.
    """
    config.set(pool_size=0)

    log("It's bad.", exception=ValueError("Example of an exception."))

    assert handler.last is not None

    assert 'local_variables' not in handler.last

def test_number_of_traceback_strings_in_log_item_data(handler):
    """
    Проверяем, что в данных о трейсбеке нет лишних строк.
    """
    config.set(pool_size=0)

    @exception_escaping
    @log
    def function():
        raise ValueError

    function()

    assert len(json.loads(handler.last['traceback'])) == 1

    assert 'in function' in json.loads(handler.last['traceback'])[0]
    assert 'test_router.py' in json.loads(handler.last['traceback'])[0]
    assert 'raise ValueError' in json.loads(handler.last['traceback'])[0]

def test_number_of_traceback_strings_in_raised_exception(handler):
    """
    Проверяем, что количество строк трейсбека соответствует ожидаемому в случае, если бы трейсбек был обрезан.
    """
    config.set(pool_size=0, traceback_cutting=True)

    @log
    def function():
        raise ValueError

    try:
        function()
    except ValueError as e:
        _, _, tb = sys.exc_info()
        counter = 0
        while tb:
            counter += 1
            tb = tb.tb_next

    assert counter == 2

def test_number_of_traceback_strings_in_raised_exception_async(handler):
    """
    Проверяем, что количество строк трейсбека в случае с декоратором над корутинной функцией соответствует ожидаемому в случае, если бы трейсбек был обрезан.
    """
    config.set(pool_size=0, traceback_cutting=True)

    @log
    async def function():
        raise ValueError

    try:
        asyncio.run(function())
    except ValueError as e:
        _, _, tb = sys.exc_info()
        counter = 0
        while tb:
            counter += 1
            tb = tb.tb_next

    assert counter == 4

def test_number_of_traceback_strings_in_raised_exception_traceback_cutting_off(handler):
    """
    Проверяем, что количество строк трейсбека соответствует ожидаемому в случае, если бы трейсбек не был обрезан, когда настройка 'traceback_cutting' выставлена в False.
    """
    config.set(pool_size=0, traceback_cutting=False)

    @log
    def function():
        raise ValueError

    try:
        function()
    except ValueError as e:
        _, _, tb = sys.exc_info()
        counter = 0
        while tb:
            counter += 1
            tb = tb.tb_next

    assert counter == 3

def test_number_of_traceback_strings_in_raised_exception_async_traceback_cutting_off(handler):
    """
    Проверяем, что количество строк трейсбека в случае с декоратором над корутинной функцией соответствует ожидаемому в случае, если бы трейсбек не был обрезан из-а настройки 'traceback_cutting' в положении False.
    """
    config.set(pool_size=0, traceback_cutting=False)

    @log
    async def function():
        raise ValueError

    try:
        asyncio.run(function())
    except ValueError as e:
        _, _, tb = sys.exc_info()
        counter = 0
        while tb:
            counter += 1
            tb = tb.tb_next

    assert counter == 5

def test_text_in_cut_traceback_strings():
    """
    Проверяем, что включенном обрезании трейсбека, в нем отсутствует строка про данные внутренние структуры Polog, а при выключенном - присутствует.
    """
    config.set(pool_size=0, traceback_cutting=False)

    @log
    def function():
        raise ValueError

    try:
        function()
    except ValueError:
        trace = json.dumps(traceback.format_tb(sys.exc_info()[2]))

    assert 'function_logger.py' in trace

    config.set(traceback_cutting=True)

    try:
        function()
    except ValueError:
        trace = json.dumps(traceback.format_tb(sys.exc_info()[2]))

    assert 'function_logger.py' not in trace

def test_text_in_log_item_traceback(handler):
    """
    Проверяем, что в итоговом записываемом в лог трейсбеке не содержится упоминаний внутренних структур Polog.
    """
    config.set(pool_size=0)

    @exception_escaping
    @log
    def function():
        raise ValueError

    function()

    assert 'function_logger.py' not in handler.last['traceback']
