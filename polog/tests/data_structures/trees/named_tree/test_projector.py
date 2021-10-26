import pytest

from polog.data_structures.trees.named_tree.tree import NamedTree
from polog.data_structures.trees.named_tree.projector import TreeProjector


def test_project_tree():
    """
    Проверяем, что новое дерево создается, не является старым деревом, в нем доступны ноды, которые указано спроецировать, и не доступны остальные.
    """
    tree = NamedTree()
    projector = TreeProjector(tree)

    tree['lol'] = 1
    tree['lol.kek'] = 2
    tree['lol.kek.cheburek'] = 3

    new_tree = projector.on(['lol.kek'])

    assert tree is not new_tree

    assert tree['lol.kek'] == new_tree['lol.kek']
    assert tree['lol.kek.cheburek'] == new_tree['lol.kek.cheburek']

    assert new_tree.get('lol') is None

def test_project_tree_of_root():
    """
    Пробуем проецировать дерево целиком.
    """
    tree = NamedTree()
    tree['lol'] = 1

    projector = TreeProjector(tree)
    with pytest.raises(ValueError):
        new_tree = projector.on(['.'])

    projector = TreeProjector(tree)
    new_tree = projector.on(['.'], not_to_root=False)
    assert new_tree['lol'] == tree['lol']

def test_not_tree_passed_to_projector_init():
    """
    Пробуем передать в конструктор не дерево, а что-то еще.
    """
    with pytest.raises(ValueError):
        projector = TreeProjector(1)
    with pytest.raises(ValueError):
        projector = TreeProjector('kek')
    with pytest.raises(ValueError):
        projector = TreeProjector([1, 2, 3])
