import pytest
from polog.core.utils.get_arg import get_arg


def test_base_empty(empty_class):
    """
    Проверка, что, если в исходном объекте нет нужного атрибута, ничего не происходит.
    """
    data = {}
    obj = empty_class()
    get_arg(obj, data, 'lol')
    assert data == {}

def test_base_full(empty_class):
    """
    Проверка, что все извлекается.
    """
    data = {}
    obj = empty_class()
    obj.lol = 'kek'
    get_arg(obj, data, 'lol')
    assert data['lol'] == 'kek'

def test_base_full_handle_key(empty_class):
    """
    Проверка, что ключ подменяется вручную.
    """
    data = {}
    obj = empty_class()
    obj.lol = 'kek'
    get_arg(obj, data, 'lol', key_name='cheburek')
    assert data['cheburek'] == 'kek'
    assert data.get('lol') is None

def test_base_full_dander(empty_class):
    """
    Проверка, что из дандер-атрибутов все извлекается, но в словарь сохраняется без дандеров.
    """
    data = {}
    obj = empty_class()
    obj.__lol__ = 'kek'
    get_arg(obj, data, '__lol__')
    assert data['lol'] == 'kek'
