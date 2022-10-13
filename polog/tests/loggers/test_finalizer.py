import pytest

from polog import config
from polog.loggers.finalizer import LoggerRouteFinalizer
from polog.errors import IncorrectUseOfTheDecoratorError, IncorrectUseLoggerError


def test_finalize_and_create_log(handler):
    """
    Создаем переменную с объектом класса LoggerRouteFinalizer, после чего удаляем ее (то есть единственную ссылку на объект).
    В этот момент должен записываться лог.
    """
    config.set(pool_size=0)

    finalizer = LoggerRouteFinalizer('lol', lol='kek')

    assert len(handler.all) == 0

    del finalizer

    assert len(handler.all) == 1

    assert handler.last['message'] == 'lol'
    assert handler.last['lol'] == 'kek'
    assert handler.last['auto'] == False

def test_create_finalizer_and_call_it(handler):
    """
    Внутри объекта LoggerRouteFinalizer есть коллбек. Проверяем, что, если его вызвать, запишется лог.
    """
    config.set(pool_size=0)

    finalizer = LoggerRouteFinalizer('lol', lol='kek')

    finalizer_callback = finalizer.finalizer

    assert len(handler.all) == 0

    finalizer_callback()

    assert len(handler.all) == 1

    assert handler.last['message'] == 'lol'
    assert handler.last['lol'] == 'kek'
    assert handler.last['auto'] == False

def test_finalizer_one_argument_not_allowed():
    """
    Проверяем, что, если вызвать объект LoggerRouteFinalizer, передав туда объект, не являющийся классом или функцией, поднимется исключение.
    """
    finalizer = LoggerRouteFinalizer('lol', lol='kek')

    with pytest.raises(IncorrectUseOfTheDecoratorError):
        finalizer('kek')

def test_finalizer_one_argument_is_allowed_function(handler):
    """
    Пробуем задекорировать с помощью объекта LoggerRouteFinalizer обычную функцию и проверяем, что это работает, то есть:
    1. Функция вызывается и возвращает ожидаемый результат.
    2. При вызове функции записывается лог.
    3. Поля записанного лога соответствуют ожидаемым.
    4. Сама по себе операция декорирования не приводит к записи лога, только вызов задекорированной функции.
    5. Логи не дублируются, после вызова функции создается ровно одна запись.
    """
    config.set(pool_size=0)

    finalizer = LoggerRouteFinalizer('lol', level=500)

    def function():
        return 3

    wrapped_function = finalizer(function)

    assert len(handler.all) == 0

    assert wrapped_function() == 3

    assert len(handler.all) == 1

    assert handler.last['message'] == 'lol'
    assert handler.last['level'] == 500
    assert handler.last['auto'] == True
    assert handler.last['function'] == 'function'
    assert handler.last['module'] == 'polog.tests.loggers.test_finalizer'
    assert handler.last['success'] == True

    assert 'time_of_work' in handler.last
    assert 'result' in handler.last
    assert 'class' not in handler.last

def test_finalizer_one_argument_is_allowed_class(handler):
    """
    Пробуем задекорировать с помощью объекта LoggerRouteFinalizer объект класса и проверяем, что это работает, то есть:
    1. Метод класса вызывается и возвращает ожидаемый результат.
    2. При вызове метода класса записывается лог.
    3. Поля записанного лога соответствуют ожидаемым.
    4. Сама по себе операция декорирования не приводит к записи лога, только вызов метода задекорированного класса.
    5. Логи не дублируются, после вызова метода создается ровно одна запись.
    """
    config.set(pool_size=0)

    finalizer = LoggerRouteFinalizer('lol', level=500)

    class LocalClass:
        def method(self):
            return 3

    wrapped_class = finalizer(LocalClass)

    assert len(handler.all) == 0

    assert wrapped_class().method() == 3

    assert len(handler.all) == 1

    assert handler.last['message'] == 'lol'
    assert handler.last['level'] == 500
    assert handler.last['auto'] == True
    assert handler.last['function'] == 'method'
    assert handler.last['class'] == 'LocalClass'
    assert handler.last['module'] == 'polog.tests.loggers.test_finalizer'
    assert handler.last['success'] == True

    assert 'time_of_work' in handler.last
    assert 'result' in handler.last

def test_finalizer_messages_conflict_silent_internal_exceptions_off():
    """
    Пробуем передать разные сообщения разными способами (в качестве позиционного аргумента и именованного).
    При значении настройки silent_internal_exceptions, равном False, должно подняться исключение.
    """
    config.set(pool_size=0, silent_internal_exceptions=False)

    with pytest.raises(IncorrectUseLoggerError):
        finalizer = LoggerRouteFinalizer('lol', message='kek')

def test_finalizer_same_messages_conflict_silent_internal_exceptions_off(handler):
    """
    Пробуем передать одинаковые сообщения разными способами (в качестве позиционного аргумента и именованного).
    При значении настройки silent_internal_exceptions, равном False, лог должен в любом случае записаться, поскольку реального конфликта значений нет.
    """
    config.set(pool_size=0, silent_internal_exceptions=False)

    finalizer = LoggerRouteFinalizer('kek', message='kek')

    def function():
        return 3

    wrapped_function = finalizer(function)

    assert wrapped_function() == 3

    assert handler.last is not None
    assert handler.last['message'] == 'kek'

def test_finalizer_messages_conflict_silent_internal_exceptions_on(handler):
    """
    Пробуем передать разные сообщения разными способами (в качестве позиционного аргумента и именованного).
    При значении настройки silent_internal_exceptions, равном True, лог должен записаться, а сообщение должно взяться из позиционного аргумента.
    """
    config.set(pool_size=0, silent_internal_exceptions=True)

    finalizer = LoggerRouteFinalizer('lol', message='kek')

    def function():
        return 3

    wrapped_function = finalizer(function)

    assert wrapped_function() == 3

    assert handler.last is not None
    assert handler.last['message'] == 'lol'

def test_logger_route_finalizer_repr():
    """
    Проверяем, что строковая репрезентация через repr() работает.
    """
    assert repr(LoggerRouteFinalizer('lol', field='kek')) == f'LoggerRouteFinalizer(field="kek", message="lol")'
    assert repr(LoggerRouteFinalizer('lol')) == f'LoggerRouteFinalizer(message="lol")'
    assert repr(LoggerRouteFinalizer(field='kek')) == f'LoggerRouteFinalizer(field="kek")'
    assert repr(LoggerRouteFinalizer()) == f'LoggerRouteFinalizer()'

def test_logger_route_finalizer_str():
    """
    Проверяем, что строковая репрезентация через str() работает.
    """
    assert str(LoggerRouteFinalizer('lol', field='kek')) == f'<A LoggerRouteFinalizer(field="kek", message="lol") object, don\'t use it!>'
    assert str(LoggerRouteFinalizer('lol')) == f'<A LoggerRouteFinalizer(message="lol") object, don\'t use it!>'
    assert str(LoggerRouteFinalizer(field='kek')) == f'<A LoggerRouteFinalizer(field="kek") object, don\'t use it!>'
    assert str(LoggerRouteFinalizer()) == f'<A LoggerRouteFinalizer() object, don\'t use it!>'

def test_finalizer_double_using(handler):
    """
    Проверяем, что при повторном вызове объекта LoggerRouteFinalizer как функции поднимается исключение.
    Также проверяем, что если удалить все ссылки на объект, то лог записан уже не будет.
    """
    config.set(pool_size=0)

    finalizer = LoggerRouteFinalizer('lol')

    def function():
        return 3

    wrapped_function = finalizer(function)

    with pytest.raises(IncorrectUseOfTheDecoratorError):
        wrapped_function_2 = finalizer(function)

    del finalizer

    assert handler.last is None
