import time
import asyncio

import pytest

from polog import log, config


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
