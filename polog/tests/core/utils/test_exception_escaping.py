import pytest

from polog.core.utils.exception_escaping import exception_escaping


def test_base_behavior():
    """
    Проверяем, что экранирование работает.
    """
    @exception_escaping
    def lol():
        raise ValueError('kek')
    lol()

def test_base_behavior():
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
