import json

import pytest

from polog.utils.json_vars import json_vars, get_item


class NotBaseType:
    def __repr__(self):
        return 'hello'

def test_base():
    """
    Проверка базовой функциональности json_vars().
    """
    to_compare = json_vars(1, 2, 3, 'test', test='lol')
    to_compare_2 = json.dumps({'args': [{'value': 1, 'type': 'int'}, {'value': 2, 'type': 'int'}, {'value': 3, 'type': 'int'}, {'value': 'test', 'type': 'str'}], 'kwargs': {'test': {'value': 'lol', 'type': 'str'}}})
    to_compare = json.loads(to_compare)
    to_compare_2 = json.loads(to_compare_2)
    assert to_compare == to_compare_2

def test_base_bool():
    """
    Проверка, что json_vars() корректно отрабатывает с типом bool.
    """
    to_compare = json_vars(False)
    to_compare_2 = json.dumps({'args': [{'value': False, 'type': 'bool'}]})
    to_compare = json.loads(to_compare)
    to_compare_2 = json.loads(to_compare_2)
    assert to_compare == to_compare_2

def test_get_item_base_types():
    """
    Проверка, что get_item() корректно отрабатывает с типами данных, стандартными для формата json.
    """
    assert get_item(1) == {'value': 1, 'type': 'int'}
    assert get_item(0.25) == {'value': 0.25, 'type': 'float'}
    assert get_item(False) == {'value': False, 'type': 'bool'}
    assert get_item('hello') == {'value': 'hello', 'type': 'str'}

def test_get_item_non_base_types():
    """
    Проверка, что get_item() корректно отрабатывает с типами данных, НЕ стандартными для формата json.
    """
    assert get_item(NotBaseType()) == {'value': 'hello', 'type': 'NotBaseType'}
