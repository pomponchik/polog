from time import sleep

import pytest

from polog import ass, config
from polog.loggers.handle.smart_assert import smart_assert as ass_2


def test_equal_imports():
    """
    Проверяем, что оба вида импортов валидны.
    """
    assert ass is ass_2

def test_raise_exception_of_smart_assert():
    """
    Проверяем, что в режиме дебага при передаче в ass() False - поднимается исключение.
    """
    config.set(debug_mode=True)

    with pytest.raises(AssertionError):
        ass(False)

def test_not_raise_exception_of_smart_assert_when_not_error():
    """
    Проверяем, что в режиме дебага при передаче в ass() True - исключение не поднимается.
    """
    config.set(debug_mode=True)
    ass(True)

def test_raise_exception_of_smart_assert_and_check_message():
    """
    Проверяем, что в поднимаемом исключении сообщение соответствует переданному в функцию.
    """
    config.set(debug_mode=True)

    try:
        ass(False, 'kek')
    except AssertionError as e:
        assert str(e) == 'kek'

def test_2_messages():
    """
    Сигнатура функции позволяет передать в нее 2 аргумента с сообщением. Но сценарий использования функции не подразумевает использование более чем 1.
    Поэтому проверяем, что в режиме silent_internal_exceptions=False поднимается исключение при попытке передать более 1 сообщения.
    """
    config.set(debug_mode=True, silent_internal_exceptions=False)

    with pytest.raises(TypeError):
        ass(False, 'kek', 'cheburek')

def test_2_messages_and_silent_internal_exceptions_mode():
    """
    Даже при неправильном использовании функции (когда в нее передаются 2 сообщения), в режиме silent_internal_exceptions=True исключение подниматься не должно.
    """
    config.set(silent_internal_exceptions=True, debug_mode=True)

    try:
        ass(False, 'kek', 'cheburek')
    except AssertionError as e:
        assert str(e) == 'kek'

def test_int_message():
    """
    Пробуем скормить не строку в качестве сообщения. Проверяем, что в этом случае оно будет преобразовано к строке.
    """
    try:
        ass(False, 1)
    except AssertionError as e:
        assert str(e) == '1'

def test_wrong_str_dander_method_in_message_object():
    """
    Пробуем передать в ass() в качестве сообщения объект, который при попытке привести его к строке или к bool поднимает исключения.
    Функция должна отработать.
    """
    config.set(debug_mode=True)

    class WrongClass:
        def __str__(self):
            raise ValueError('kek')
        def __repr__(self):
            raise ValueError('kek')
        def __nonzero__(self):
            raise ValueError('kek')

    try:
        ass(False, WrongClass())
    except AssertionError as e:
        assert str(e) == 'False'

def test_wrong_str_dander_method_in_expression_result_object():
    """
    Пробуем передать поднимающий при попытке привести к строке или к bool объект в качестве результата выражения.
    Должно все равно отработать, но написать в вообщении, что невозможно извлечь данные для лога.
    """
    config.set(debug_mode=True)

    class WrongClass:
        def __str__(self):
            raise ValueError('kek')
        def __repr__(self):
            raise ValueError('kek')
        def __nonzero__(self):
            raise ValueError('kek')

    try:
        kek = ass(WrongClass())
    except AssertionError as e:
        assert str(e) == 'It is impossible to extract data for the log.'

    try:
        ass(WrongClass(), WrongClass())
    except AssertionError as e:
        assert str(e) == 'It is impossible to extract data for the log.'

def test_write_false_to_log_of_smart_assert(handler):
    """
    Проверяем, что в режиме debug_mode=False:
    1. Записывается лог.
    2. Исключение не поднимается.
    3. Без переданного сообщения используется сериализация переданного выражения.
    """
    config.set(debug_mode=False, pool_size=0)

    ass(False)

    assert handler.last['message'] == 'False'

def test_write_empty_list_to_log_of_smart_assert(handler):
    """
    Проверяем, что в режиме debug_mode=False:
    1. Записывается лог.
    2. Исключение не поднимается.
    3. Без переданного сообщения используется сериализация переданного выражения.
    """
    config.set(debug_mode=False, pool_size=0)

    ass([])

    assert handler.last['message'] == '[]'

def test_write_string_message_to_log_of_smart_assert(handler):
    """
    Проверяем, что в режиме debug_mode=False:
    1. Записывается лог.
    2. Исключение не поднимается.
    3. С переданным сообщением, оно сохраняется в лог.
    """
    config.set(debug_mode=False, pool_size=0)

    ass(False, 'kek')

    assert handler.last['message'] == 'kek'

def test_auto_flag_in_smart_assert(handler):
    """
    Проверяем, что флаг "auto" для логов, записанных через ассерт, проставляется в False.
    """
    config.set(debug_mode=False, pool_size=0)
    
    ass(False, 'kek')

    assert handler.last['auto'] == False
