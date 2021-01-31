import pytest
from polog.handlers.memory.saver import memory_saver


handler = memory_saver()

def test_singleton():
    assert memory_saver() is memory_saver()

def test_add_empty_args():
    handler((None, None), **{'message': 'hello'})
    assert handler.last.fields['message'] == 'hello'

def test_add_full_args():
    handler(((1, 2, 3), {'lol': 'kek'}), **{'message': 'hello'})
    assert handler.last.fields['message'] == 'hello'
    assert handler.last.args == (1, 2, 3)
    assert handler.last.kwargs == {'lol': 'kek'}

def test_clean():
    handler.clean()
    assert len(handler.all) == 0
