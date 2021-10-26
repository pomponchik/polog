from sys import getrecursionlimit

import pytest

from polog.data_structures.trees.named_tree.printer import TreePrinter
from polog.data_structures.trees.named_tree.tree import NamedTree


def test_recursion_limit():
    """
    Проверяем, что при слишком глубоком дереве не поднимается RecursionError, а все же возвращается строковое представление объекта (болванка без данных).
    """
    tree = NamedTree()

    for number in range(getrecursionlimit() + 1):
        node_name = ('k.' * (number + 1))[:-1]
        tree[node_name] = 'kek'

    assert str(tree) == '<NamedTree very big object>'

def test_base_behavior():
    """
    Проверка основных параметров строкового представления дерева.
    """
    tree = NamedTree()

    tree['lol'] = 'kek'
    tree['kek'] = 'cheburek'
    tree['kek.pek'] = 'berebek'

    representation = str(tree)

    assert type(representation) is str
    assert representation.startswith('<NamedTree')
    assert representation.endswith('>')

    assert len(tree) + 2 == len(representation.split('\n'))

    assert 'lol' in representation
    assert 'kek' in representation
    assert 'pek' in representation

def test_print_empty_tree():
    """
    Проверка, что если в дереве нет ни одного сохраненного значения, оно распечатывается в виде "болванки".
    """
    tree = NamedTree()

    assert str(tree) == '<NamedTree empty object>'
