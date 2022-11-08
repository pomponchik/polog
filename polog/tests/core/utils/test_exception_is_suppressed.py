import pytest

from polog.core.utils.exception_is_suppressed import exception_is_suppressed


def test_suppress_exception_subclasses_on_value_error_and_value_error():
    """
    Проверяем, что, при включенной настройке 'suppress_exception_subclasses', при полном совпадении типов исключений - возвращается True.
    """
    assert exception_is_suppressed(ValueError(), [ValueError], {'suppress_exception_subclasses': True}) == True

def test_suppress_exception_subclasses_on_value_error_and_other_error():
    """
    Проверяем, что, при включенной настройке 'suppress_exception_subclasses', при не совпадении типов исключений - возвращается False.
    """
    assert exception_is_suppressed(ValueError(), [TypeError], {'suppress_exception_subclasses': True}) == False

def test_suppress_exception_subclasses_off_value_error_and_other_error():
    """
    Проверяем, что, при выключенной настройке 'suppress_exception_subclasses', при не совпадении типов исключений - возвращается False.
    """
    assert exception_is_suppressed(ValueError(), [TypeError], {'suppress_exception_subclasses': False}) == False

def test_suppress_exception_subclasses_off_value_error_and_value_error():
    """
    Проверяем, что, при выключенной настройке 'suppress_exception_subclasses', при полном совпадении типов исключений - возвращается True.
    """
    assert exception_is_suppressed(ValueError(), [ValueError], {'suppress_exception_subclasses': False}) == True

def test_suppress_exception_subclasses_on_value_error_and_exception():
    """
    Проверяем, что, при включенной настройке 'suppress_exception_subclasses', если переданное исключение относится к подклассу одного из подавляемых - возвращается True.
    """
    assert exception_is_suppressed(ValueError(), [Exception], {'suppress_exception_subclasses': True}) == True

def test_suppress_exception_subclasses_off_value_error_and_exception():
    """
    Проверяем, что, при выключенной настройке 'suppress_exception_subclasses', если переданное исключение относится к подклассу одного из подавляемых - возвращается False.
    """
    assert exception_is_suppressed(ValueError(), [Exception], {'suppress_exception_subclasses': False}) == False
