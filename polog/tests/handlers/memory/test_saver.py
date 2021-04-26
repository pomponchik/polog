import pytest
from polog.handlers.memory.saver import memory_saver


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
    handler((None, None), **{'message': 'hello'})
    assert handler.last.fields['message'] == 'hello'
    assert len(handler.all) > 0

def test_add_full_args():
    """
    Проверка, что запись лога в память происходит.
    """
    handler(((1, 2, 3), {'lol': 'kek'}), **{'message': 'hello'})
    assert handler.last.fields['message'] == 'hello'
    assert handler.last.args == (1, 2, 3)
    assert handler.last.kwargs == {'lol': 'kek'}

def test_clean():
    """
    Проверка, что список логов очищается.
    """
    handler((None, None), **{'message': 'hello'})
    handler.clean()
    assert len(handler.all) == 0
    assert handler.last is None

def test_add_to_all():
    """
    Проверка, что список handler.all заполняется логами.
    """
    handler.clean()
    handler((None, None), **{'message': 'hello'})
    assert len(handler.all) > 0

def test_getargs():
    """
    Проверка, что можно получить доступ к полям лога без обращения напрямую к словарю.
    """
    handler.clean()
    handler((None, None), **{'message': 'hello'})
    assert handler.last is not None
    assert handler.last.fields['message'] is not None
    assert handler.last.fields['message'] == handler.last['message']
