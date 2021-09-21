import pytest
from polog.data_structures.trees.named_tree.tree import NamedTree


def test_set_and_get():
    """
    Сохраняем значения в дерево и получаем их обратно по ключам.
    """
    tree = NamedTree()
    tree['kek'] = 'lol'
    assert tree['kek'] == 'lol'
    tree['kek.cheburek'] = 'lolkek'
    assert tree['kek.cheburek'] == 'lolkek'
