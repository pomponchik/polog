import time
import asyncio

import pytest

from polog import log, flog, unlog, config
from polog.errors import IncorrectUseOfTheDecoratorError


def test_unlog_before(handler):
    """
    Проверяем ситуацию, когда @unlog стоит до логирующего декоратора.
    """
    @unlog
    @flog(message='base text', level=100)
    def function():
        pass

    function()
    time.sleep(0.0001)

    assert len(handler.all) == 0

def test_unlog_with_empty_brackets(handler):
    """
    Проверяем, что с пустыми скобками декоратор работает точно так же, как без них (то есть по аналогии с тестом test_unlog_before).
    """
    @unlog()
    @flog(message='base text', level=100)
    def function():
        pass

    function()
    time.sleep(0.0001)

    assert len(handler.all) == 0

def test_unlog_before_async(handler):
    """
    Тест аналогичен обычному test_unlog_before, но оборачиваем мы на этот раз корутинную функцию.
    """
    @unlog
    @flog(message='base text', level=100)
    async def function():
        pass

    asyncio.run(function())
    time.sleep(0.0001)

    assert len(handler.all) == 0

def test_unlog_after(handler):
    """
    Когда @unlog после логирующего декоратора.
    """
    @flog(message='base text', level=100)
    @unlog
    def function():
        pass

    function()
    time.sleep(0.0001)

    assert len(handler.all) == 0

def test_unlog_multiple(handler):
    """
    Когда логирующие декораторы по нескольку штук с обеих сторон от @unlog.
    """
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @unlog
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    def function():
        return True

    function()
    time.sleep(0.0001)

    assert len(handler.all) == 0

def test_working():
    """
    Проверяем, что декоратор не ломает поведение функции.
    """
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @unlog
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    @flog(message='base text', level=100)
    def function():
        return True

    assert function() == True

def test_double_forbidden(handler):
    """
    Проверяем, что двойное наложение декоратора не ломает его работу.
    """
    @unlog
    @unlog
    @flog(message='base text', level=100)
    def function():
        pass

    function()
    time.sleep(0.0001)

    assert len(handler.all) == 0

def test_unlog_class(handler):
    """
    Пробуем запретить логирование в целом классе.
    Проверяем, что это работает.
    """
    config.set(pool_size=0)

    @unlog
    class Lol:
        @flog
        def kek(self, a, b):
            return a + b

    assert Lol().kek(2, 3) == 5
    assert handler.last is None

def test_incorrect_using_of_unlog():
    """
    Проверяем, что декоратор @unlog ругается, если передать туда что-то не то.
    """
    with pytest.raises(IncorrectUseOfTheDecoratorError):
        unlog('kek')
    with pytest.raises(IncorrectUseOfTheDecoratorError):
        unlog(unlog, unlog)

def test_unlog_local_flag_full_false_global_false(handler):
    """
    Проверяем, что, если флаг full_unlog и локально и глобально выставлен в False, ручные логи записываются.
    """
    config.set(pool_size=0, full_unlog=False)

    @unlog(full=False)
    def function():
        log('kek')

    function()

    assert handler.last is not None

def test_unlog_local_flag_full_true_global_false(handler):
    """
    Если флаг full_unlog локально выставлен в True, а глобально - False, ручные логи не записываются.
    """
    config.set(pool_size=0, full_unlog=False)

    @unlog(full=True)
    def function():
        log('kek')

    function()

    assert handler.last is None

def test_unlog_local_flag_full_false_global_true(handler):
    """
    Если флаг full_unlog локально выставлен в False, а глобально - True, ручные логи записываются.
    """
    config.set(pool_size=0, full_unlog=True)

    @unlog(full=False)
    def function():
        log('kek')

    function()

    assert handler.last is not None

def test_unlog_local_flag_full_true_global_true(handler):
    """
    Если флаг full_unlog и локально и глобально выставлен в True, ручные логи не записываются.
    """
    config.set(pool_size=0, full_unlog=True)

    @unlog(full=True)
    def function():
        log('kek')

    function()

    assert handler.last is None

def test_unlog_local_flag_full_false_global_false_async(handler):
    """
    Тест идентичен test_unlog_local_flag_full_false_global_false, но в декоратор оборачивается корутинная функция вместо обычной.
    """
    config.set(pool_size=0, full_unlog=False)

    @unlog(full=False)
    async def function():
        log('kek')

    asyncio.run(function())

    assert handler.last is not None

def test_unlog_local_flag_full_true_global_false_async(handler):
    """
    Тест идентичен test_unlog_local_flag_full_true_global_false, но в декоратор оборачивается корутинная функция вместо обычной.
    """
    config.set(pool_size=0, full_unlog=False)

    @unlog(full=True)
    async def function():
        log('kek')

    asyncio.run(function())

    assert handler.last is None

def test_unlog_local_flag_full_false_global_true_async(handler):
    """
    Тест идентичен test_unlog_local_flag_full_false_global_true, но в декоратор оборачивается корутинная функция вместо обычной.
    """
    config.set(pool_size=0, full_unlog=True)

    @unlog(full=False)
    async def function():
        log('kek')

    asyncio.run(function())

    assert handler.last is not None

def test_unlog_local_flag_full_true_global_true_async(handler):
    """
    Тест идентичен test_unlog_local_flag_full_true_global_true, но в декоратор оборачивается корутинная функция вместо обычной.
    """
    config.set(pool_size=0, full_unlog=True)

    @unlog(full=True)
    async def function():
        log('kek')

    asyncio.run(function())

    assert handler.last is None

def test_unlog_outside_of_unlogged_function(handler):
    """
    Проверяем, что если вызов log() в стеке вызовов функций находится выше декоратора @unlog, он не аффектит то, что находится выше.
    """
    config.set(pool_size=0, full_unlog=True)

    @unlog(full=True)
    def function_2():
        log('kek')

    def function():
        function_2()
        log('lol')

    function()

    assert handler.last is not None
    assert len(handler.all) == 1
    assert handler.last['message'] == 'lol'

def test_unlog_outside_of_unlogged_function_wrapped_by_log_decorator(handler):
    """
    Тест аналогичен test_unlog_outside_of_unlogged_function, но декоратор @unlog теперь окружен декораторами @log.
    """
    config.set(pool_size=0, full_unlog=True)

    @log(message='lol 2')
    @unlog(full=True)
    @log(message='kek 2')
    def function_2():
        log('kek')

    def function():
        function_2()
        log('lol')

    function()

    assert handler.last is not None
    assert len(handler.all) == 1
    assert handler.last['message'] == 'lol'

def test_unlog_outside_of_unlogged_function_wrapped_by_log_decorator_async(handler):
    """
    Тест аналогичен test_unlog_outside_of_unlogged_function_wrapped_by_log_decorator, но теперь с корутинными функциями.
    """
    config.set(pool_size=0, full_unlog=True)

    @log(message='lol 2')
    @unlog(full=True)
    @log(message='kek 2')
    async def function_2():
        log('kek')

    async def function():
        await function_2()
        log('lol')

    asyncio.run(function())

    assert handler.last is not None
    assert len(handler.all) == 1
    assert handler.last['message'] == 'lol'

def test_unlog_outside_of_unlogged_function_multiple_wrapped_by_log_decorator(handler):
    """
    Тест аналогичен test_unlog_outside_of_unlogged_function_wrapped_by_log_decorator, но декоратор @unlog продублирован сам и окружен продублированными декораторами @log.
    """
    config.set(pool_size=0, full_unlog=True)

    @log(message='lol 1')
    @log(message='lol 2')
    @log(message='lol 3')
    @log(message='lol 4')
    @log(message='lol 5')
    @unlog(full=True)
    @unlog(full=True)
    @unlog(full=True)
    @unlog(full=True)
    @log(message='kek 1')
    @log(message='kek 2')
    @log(message='kek 3')
    @log(message='kek 4')
    @log(message='kek 5')
    @log(message='kek 6')
    @log(message='kek 7')
    @log(message='kek 8')
    def function_2():
        log('kek')

    def function():
        function_2()
        log('lol')

    function()

    assert handler.last is not None
    assert len(handler.all) == 1
    assert handler.last['message'] == 'lol'

def test_unlog_over_other_decorator(handler):
    """
    Пробуем разместить @unlog над другим декоратором, который "перекрывает" @log.
    За счет контекстной переменной это должно сработать.
    """
    config.set(pool_size=0, full_unlog=True)

    def other_decorator(function):
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        return wrapper

    @unlog
    @other_decorator
    @log(message='lol')
    def function():
        log('kek')

    function()

    assert handler.last is None

def test_minus_unlog_is_log():
    """
    Отрицание объекта unlog должно давать log.
    Это нужно для симметрии синтаксиса (чтобы двойное отрицание log давало снова log).
    """
    assert -unlog is log
