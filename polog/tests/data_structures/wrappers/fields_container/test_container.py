import pytest

from polog.data_structures.wrappers.fields_container.container import FieldsContainer


def test_wrapper_items_iteration_base():
    """
    Проверяем базовый случай, что два словаря с непересекающимися ключами объединяются.
    """
    assert {key: value for key, value in FieldsContainer({'lol': 'kek'}, {'cheburek': 'perekek'}).items()} == {'lol': 'kek', 'cheburek': 'perekek'}

def test_wrapper_items_iteration_intersection():
    """
    Немного усложняем. В двух словарях есть одинаковый ключ 'pek' с разными значениями.
    В итоге при итерации значение должно подставиться из основного словаря.
    """
    assert {key: value for key, value in FieldsContainer({'lol': 'kek', 'pek': 'mek'}, {'cheburek': 'perekek', 'pek': 'zek'}).items()} == {'lol': 'kek', 'pek': 'mek', 'cheburek': 'perekek'}

def test_wrapper_items_iteration_intersection_len():
    """
    Проверяем, что при пересекающихся ключах в словарях они не дублируются при итерации.
    """
    items = list(FieldsContainer({'lol': 'kek', 'pek': 'mek'}, {'cheburek': 'perekek', 'pek': 'zek'}).items())
    assert len(items) == 3

def test_wrapper_iteration_base():
    """
    Еще один базовый случай, что два непересекающихся множества ключей двух словарей при итерации объединяются.
    """
    assert list(FieldsContainer({'lol': 'kek'}, {'cheburek': 'perekek'})) == ['lol', 'cheburek']

def test_wrapper_iteration_intersection():
    """
    Еще один базовый случай, что два непересекающихся множества ключей двух словарей при итерации объединяются.
    """
    assert list(FieldsContainer({'lol': 'kek', 'pek': 'mek'}, {'cheburek': 'perekek', 'pek': 'zek'})) == ['lol', 'pek', 'cheburek']
