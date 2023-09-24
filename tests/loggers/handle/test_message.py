import time
import asyncio

import pytest

from polog import log, message, field, config


def test_basic_message(handler):
    """
    Проверяем, что дефолтное сообщение подменяется новым.
    """
    config.set(level=1)

    @log(message='base text')
    def normal_function():
        message('new text', level=5)
        return True

    normal_function()

    time.sleep(0.0001)
    assert handler.last['message'] == 'new text'

def test_basic_message_async(handler):
    """
    Тест аналогичен test_basic_message, но message() используется внутри корутинной функции.
    """
    config.set(level=1)

    @log(message='base text')
    async def normal_function():
        message('new text', level=5)
        return True

    asyncio.run(normal_function())

    time.sleep(0.0001)
    assert handler.last['message'] == 'new text'

def test_basic_message_exception(handler):
    """
    Проверяем работу с исключениями.
    """
    config.set(level=1)

    @log(message='base text')
    def error_function():
        try:
            raise ValueError('exception text')
        except ValueError as e:
            message(e=e)

    @log(message='base text')
    def error_function_2():
        try:
            raise ValueError('exception text 2')
        except ValueError as e:
            message(exception=e)

    @log(message='base text')
    def error_function_3():
        message(exception=ValueError('new message'))

    error_function()
    time.sleep(0.01)
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'exception text'
    handler.clean()

    error_function_2()
    time.sleep(0.01)
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'exception text 2'
    handler.clean()

    error_function_3()
    time.sleep(0.01)
    assert handler.last['exception_type'] == 'ValueError'
    assert handler.last['exception_message'] == 'new message'

def test_message_affects(handler):
    """
    Пробуем зааффектить одним вызовом message() другой.
    """
    config.set(level=1, pool_size=0)

    def function_without_flog():
        message('lol', local_variables='kek')

    @log
    def function_with_flog():
        message('lolkek')

    function_without_flog()
    function_with_flog()

    assert handler.last.get('local_variables') is None

def test_message_with_another_field(handler):
    """
    Проверяем, что работает прописывание собственных значений для пользовательских полей.
    """
    config.set(level=1, pool_size=0)

    def extractor(log_item):
        pass
    config.add_fields(lolkek=field(extractor))

    @log(message='lolkek')
    def function():
        message('lolkek', lolkek='lolkek')

    function()

    assert handler.last['lolkek'] == 'lolkek'

def test_message_unknown_argument(handler):
    """
    Проверяем, что в message можно передать неизвестный именной аргумент.
    """
    @log
    def function():
        message('lolkek', unknown_argument='kek')

    config.set(silent_internal_exceptions=True, unknown_fields_in_handle_logs=True)

    function()

    assert handler.last['unknown_argument'] == 'kek'

def test_wrong_type():
    """
    Проверяем, что если в одно из стандартных полей подать переменную неправильного типа, поднимется исключение.
    """
    @log
    def function():
        message('lolkek', success='kek')

    config.set(silent_internal_exceptions=False, unknown_fields_in_handle_logs=True)

    with pytest.raises(ValueError):
        function()

def test_message_unhandled_exception(handler):
    """
    Проверяем, что извлечение сообщений работает в том числе в случае необработанного внутри функции исключения.
    """
    @log
    def function():
        message('kek')
        raise ValueError

    with pytest.raises(ValueError):
        function()

    assert handler.last is not None
    assert handler.last['message'] == 'kek'

def test_message_unhandled_exception_async(handler):
    """
    Тест аналогичен test_message_unhandled_exception, но message() используется внутри корутинной функции.
    """
    @log
    async def function():
        message('kek')
        raise ValueError

    with pytest.raises(ValueError):
        asyncio.run(function())

    assert handler.last is not None
    assert handler.last['message'] == 'kek'
