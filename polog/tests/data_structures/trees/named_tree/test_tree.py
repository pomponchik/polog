import pytest
from polog.data_structures.trees.named_tree.tree import NamedTree


def test_set_and_get():
    tree = NamedTree()
    tree['kek'] = 'lol'
    assert tree['kek'] == 'lol'
    tree['kek.cheburek'] = 'lol'
    assert tree['kek.cheburek'] == 'lol'
