import time

import pytest

from polog.core.utils.time_limit import time_limit


def test_integer():
    """
    Проверяем, что лимит устанавливается и срабатывает с числом в качестве аргумента.
    """
    quant = 0.001
    function = lambda number: [time.sleep(quant) for x in range(number)]

    wrapper = time_limit(quant)
    wrapped_function = wrapper(function)
    with pytest.raises(TimeoutError):
        wrapped_function(5)

    wrapper = time_limit(quant * 10)
    wrapped_function = wrapper(function)
    wrapped_function(5)

def test_function_as_parameter():
    """
    Проверяем, что лимит устанавливается и срабатывает с функцией в качестве аргумента.
    """
    quant = 0.001
    function = lambda number: [time.sleep(quant) for x in range(number)]

    wrapper = time_limit(lambda: quant)
    wrapped_function = wrapper(function)
    with pytest.raises(TimeoutError):
        wrapped_function(5)

    wrapper = time_limit(lambda: quant * 10)
    wrapped_function = wrapper(function)
    wrapped_function(5)

def test_error_signature_function():
    """
    Проверяем, что функция с некорректной сигнатурой не принимается.
    """
    def test(kek):
        pass
    with pytest.raises(ValueError):
        wrapper = time_limit(test)

    test = lambda x: None
    with pytest.raises(ValueError):
        wrapper = time_limit(test)

def test_wrong_numbers():
    """
    Проверяем, что, при попытке передать в конструктор декоратора недействительное значение, поднимается ValueError.
    """
    with pytest.raises(ValueError):
        @time_limit(-1)
        def kek():
            pass
    with pytest.raises(ValueError):
        # Нулевой таймаут тоже классифицируется как ошибка.
        @time_limit(0)
        def kek():
            pass

def test_wrong_object():
    """
    Проверяем, что, при попытке передать в конструктор декоратора не число и не функция, поднимается ValueError.
    """
    with pytest.raises(ValueError):
        @time_limit('kek')
        def kek():
            pass

def test_wrong_number_in_action():
    """
    В случае, если переданная аргументом функция возвращает недействительное значение, она должна просто отрабатывать без таймаута.
    Проверяем, что это так и происходит.
    """
    flag = False
    @time_limit(lambda: -1)
    def function():
        nonlocal flag
        flag = True
    function()
    assert flag == True
