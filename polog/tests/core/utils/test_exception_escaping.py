import asyncio

import pytest

from polog.core.utils.exception_escaping import exception_escaping


def test_base_escaping():
    """
    Проверяем, что экранирование работает на обычной функции.
    """
    @exception_escaping
    def lol():
        raise ValueError('kek')
    
    lol()

def test_async_escaping():
    """
    Проверяем, что экранирование работает на корутинной функции.
    """
    @exception_escaping
    async def lol():
        raise ValueError('kek')

    asyncio.run(lol())

def test_base_behaviour():
    """
    Проверяем, что экранирование не нарушает работу задекорированной функции.
    """
    cheburek = 0

    @exception_escaping
    def lol():
        nonlocal cheburek
        cheburek = 1
        raise ValueError('kek')

    lol()
    assert cheburek == 1

def test_async_behaviour():
    """
    Проверяем, что экранирование не нарушает работу задекорированной корутинной функции.
    """
    cheburek = 0

    @exception_escaping
    async def lol():
        nonlocal cheburek
        cheburek = 1
        raise ValueError('kek')

    asyncio.run(lol())
    assert cheburek == 1
