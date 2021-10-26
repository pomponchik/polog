import pytest

from polog.handlers.memory.saver import memory_saver
from polog.core.log_item import LogItem


handler = memory_saver()

def test_singleton():
    """
    Проверка, что memory_saver - синглтон.
    """
    assert memory_saver() is memory_saver()

def test_add_empty_args():
    """
    Проверка, что запись лога в память происходит.
    """
    handler({'message': 'hello'})
    assert handler.last['message'] == 'hello'
    assert len(handler.all) > 0

def test_add_full_args():
    """
    Проверка, что запись лога в память происходит.
    """
    log = LogItem()
    log.set_data({'message': 'hello'})
    log.set_function_input_data((1, 2, 3), {'lol': 'kek'})

    handler(log)

    assert handler.last['message'] == 'hello'
    assert handler.last.function_input_data.args == (1, 2, 3)
    assert handler.last.function_input_data.kwargs == {'lol': 'kek'}

def test_clean():
    """
    Проверка, что список логов очищается.
    """
    log = LogItem()
    log.set_data({'message': 'hello'})

    handler(log)
    handler.clean()

    assert len(handler.all) == 0
    assert handler.last is None

def test_add_to_all():
    """
    Проверка, что список handler.all заполняется логами.
    """
    log = LogItem()
    log.set_data({'message': 'hello'})

    handler.clean()
    handler(log)
    assert len(handler.all) > 0

def test_getargs():
    """
    Проверка, что можно получить доступ к полям лога без обращения напрямую к словарю.
    """
    log = LogItem()
    log.set_data({'message': 'hello'})

    handler.clean()
    handler(log)
    assert handler.last is not None
    assert handler.last['message'] is not None
    assert handler.last.fields['message'] == handler.last['message']
