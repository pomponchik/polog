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

def test_iter():
    """
    Проверяем, что при итерации по дереву все хранящиеся в нем значения выводятся, а также проверяем, что это происходит именно в порядке обхода в ширину.
    """
    tree = NamedTree()
    tree['kek'] = 'lol'
    tree['kek.cheburek'] = 'lolkek'
    assert [x for x in tree] == ['lol', 'lolkek']
    tree['pek'] = 'shmek'
    assert [x for x in tree] == ['lol', 'shmek', 'lolkek']
    tree['pek.shmek'] = 'perekek'
    assert [x for x in tree] == ['lol', 'shmek', 'lolkek', 'perekek']

def test_iter_empty():
    """
    Проверяем, что при итерации по дереву, в котором нет ни одного значения, длина коллекции равна нолю.
    """
    tree = NamedTree()
    tree.childs['lol'] = NamedTree()
    tree.childs['kek'] = NamedTree()
    assert list(tree) == []

def test_len():
    """
    Проверяем, что длина коллекции считается корректно.

    Пустые ноды не учитываются, но если у них есть не пустые потомки - потомки учитываются.
    """
    tree = NamedTree()
    assert len(tree) == 0
    tree['kek'] = 'lol'
    assert len(tree) == 1
    tree['kek.cheburek'] = 'lolkek'
    assert len(tree) == 2
    tree['pek'] = 'shmek'
    assert len(tree) == 3
    tree['pek.shmek'] = 'perekek'
    assert len(tree) == 4
    empty_node = NamedTree()
    tree.childs['perekekoperekek'] = empty_node
    assert len(tree) == 4
    empty_node['sas'] = 'shmas'
    assert len(tree) == 5
