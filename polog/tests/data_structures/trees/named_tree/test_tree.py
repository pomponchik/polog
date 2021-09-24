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

def test_contains():
    """
    Проверяем, что оператор "in" работает.
    """
    tree = NamedTree()
    assert 'kek' not in tree
    tree['kek'] = 'lol'
    assert 'kek' in tree
    tree['kek.cheburek'] = 'lolkek'
    assert 'kek.cheburek' in tree
    assert 'shmek' not in tree

def test_del():
    """
    Проверяем, что оператор "del" работает.
    """
    tree = NamedTree()

    with pytest.raises(KeyError):
        del tree['kek']

    tree['kek'] = 'lol'
    assert len(tree) == 1
    with pytest.raises(KeyError):
        del tree['cheburek']
    del tree['kek']
    assert len(tree) == 0

    # Проверка, что "пустые" ноды вырезаются, когда они не ведут к ноде, содержащей значение.
    child_1 = NamedTree()
    child_2 = NamedTree()
    child_3 = NamedTree()
    tree.childs['shmek'] = child_1
    child_1.parent = tree
    child_1.childs['shmek'] = child_2
    child_2.parent = child_1
    child_2.childs['shmek'] = child_3
    child_3.parent = child_2
    child_3['kek'] = 'cheburek'
    assert len(tree) == 1
    del tree['shmek.shmek.shmek.kek']
    assert len(tree) == 0
    assert len(tree.childs) == 0
