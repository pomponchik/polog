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

def test_get_name_and_full_name():
    """
    Проверяем, что имя ноды и полное имя ноды выводятся корректно.

    Имя ноды - это идентификатор одной ноды.
    Полное имя ноды состоит из имен всех предков данной ноды + имени ноды.

    В случае, если в отдельное дерево выделена ветка другого дерева, полное имя ноды будет простираться до корневой ноды исходного дерева.
    """
    tree = NamedTree()

    assert tree.name is None

    assert tree.get_full_name() == '.'
    assert tree.get_full_name(default='kek') == 'kek'
    assert NamedTree(keys_separator='/').get_full_name() == '/'

    tree['kek'] = 'cheburek'
    node = tree.search_node(['kek'])
    assert node.get_full_name() == 'kek'
    assert node.name == 'kek'

    tree['lol'] = 'kek'
    tree['lol.kek'] = 'cheburek'
    node = tree.search_node(['lol', 'kek'])
    assert node.get_full_name() == 'lol.kek'
    assert node.name == 'kek'

    assert tree.name is None

def test_get_empty_or_not():
    """
    Проверяем, что методы .get() и .__getitem__() ведут себя по-разному.

    .get() при несуществующем ключе возвращает None.
    .__getitem__() поднимает KeyError.
    """
    tree = NamedTree()

    with pytest.raises(KeyError):
        tree['kek']

    assert tree.get('kek') is None

    tree['kek'] = 'cheburek'
    assert tree.get('kek') == 'cheburek'
    assert tree['kek'] == 'cheburek'

def test_delete_value():
    """
    Проверяем, что метод .delete_value() подменяет хранящееся в ноде значение на None.
    """
    tree = NamedTree()

    tree.value = 'kek'
    assert tree.value == 'kek'
    tree.delete_value()
    assert tree.value is None

def test_set_none():
    """
    Проверяем, что сохранить в дерево None нельзя.
    """
    tree = NamedTree()

    with pytest.raises(ValueError):
        tree['kek'] = None

def test_key_checker():
    """
    Проверяем, что работает дефолтная проверка ключей, а также что можно установить свою и она тоже будет работать.
    """
    tree = NamedTree()
    with pytest.raises(KeyError):
        tree[' kek'] = 'cheburek'

    tree = NamedTree(key_checker=lambda key: key=='lol')
    tree['lol'] = 'kek'
    with pytest.raises(KeyError):
        tree['not_lol'] = 'kek'

def test_value_checker():
    """
    Можно установить запрет на сохранение определенных значений в дереве (помимо None). Проверяем, что он работает.
    """
    tree = NamedTree()
    tree['kek'] = 'cheburek'

    tree = NamedTree(value_checker=lambda x: x == 'cheburek')
    tree['kek'] = 'cheburek'
    with pytest.raises(ValueError):
        tree['not_kek'] = 'not cheburek'

def test_re_set():
    """
    Пробуем сохранить два разных значения по одному ключу.
    Они должны перезаписываться.
    """
    tree = NamedTree()

    tree['kek'] = 'cheburek'
    assert tree['kek'] == 'cheburek'
    tree['kek'] = 'not cheburek'
    assert tree['kek'] == 'not cheburek'

def test_search_node():
    """
    Проверяем, что поиск ноды по списку ключей работает.
    """
    tree = NamedTree()

    assert tree.search_node(['kek']) is None

    tree['kek'] = 'cheburek'
    assert type(tree.search_node(['kek'])) is NamedTree
    assert tree.search_node(['kek']).value == 'cheburek'

    tree['kek.shmek'] = 'chebukek'
    assert type(tree.search_node(['kek', 'shmek'])) is NamedTree
    assert tree.search_node(['kek', 'shmek']).value == 'chebukek'

def test_search_or_create_node():
    """
    Проверяем, что при отсутствии ноды по заданным ключам она создается, а при наличии - возвращается существующая.
    """
    tree = NamedTree()

    node = tree.search_or_create_node(['kek', 'shmek'])
    assert type(node) is NamedTree
    assert node.value is None
    assert node.name == 'shmek'

    tree['cheburek.kek'] = 'perekek'
    node = tree.search_or_create_node(['cheburek', 'kek'])
    assert type(node) is NamedTree
    assert node.value == 'perekek'
    assert node.name == 'kek'

def test_create_child():
    """
    Проверяем, что потомок ноды успешно создается, и все базовые свойства наследуются.
    """
    tree = NamedTree()

    node = tree.create_child('kek')
    assert tree.childs['kek'] is node
    assert node.parent is tree
    assert type(node) is NamedTree
    assert node.value is None
    assert node.keys_separator == tree.keys_separator
    assert node.key_checker is tree.key_checker
    assert node.value_checker is tree.value_checker
    assert node.name == 'kek'

def test_get_converted_keys():
    """
    Проверяем, что ключ сепарируется корректно.
    """
    tree = NamedTree()
    assert tree.get_converted_keys('kek.cheburek') == ['kek', 'cheburek']

    tree = NamedTree(keys_separator='/')
    assert tree.get_converted_keys('kek/cheburek') == ['kek', 'cheburek']

    tree = NamedTree(keys_separator='/')
    with pytest.raises(KeyError):
        tree.get_converted_keys('kek.cheburek')

def test_get_converted_keys_of_root():
    """
    В случае с ключом в виде символа-разделителя, должен возвращаться список с ним же.
    """
    tree = NamedTree(keys_separator='.')
    assert tree.get_converted_keys('.') == ['.']

def test_wrong_key():
    """
    Проверем, что не-строки нельзя использовать в качестве ключей.
    """
    tree = NamedTree()

    with pytest.raises(KeyError):
        node = tree[6]

    with pytest.raises(KeyError):
        node = tree.get(6)

def test_put_node_to_root():
    """
    Пробуем поместить новую ноду корень текущего дерева. Поскольку это невозможно, метод .put_node() просто вернет ее в качестве нового дерева.
    """
    tree = NamedTree()
    node_to_put = NamedTree()

    assert tree.put_node('.', node_to_put) is node_to_put

def test_put_node():
    """
    Пробуем вставить ноду в дерево.
    """
    path = 'lol.kek'
    tree = NamedTree()
    node_to_put = NamedTree()

    assert tree.put_node(path, node_to_put) is tree
    assert tree.search_node(tree.get_converted_keys(path)) is node_to_put

def test_put_node_replace():
    """
    Пробуем вставить ноду в дерево, заместив другую ноду. Проверяем, что замена происходит.
    """
    path = 'lol.kek'
    tree = NamedTree()
    node_to_put = NamedTree()

    tree.put_node(path, NamedTree())
    assert tree.put_node(path, node_to_put) is tree
    assert tree.search_node(tree.get_converted_keys(path)) is node_to_put

def test_get_root_of_tree():
    """
    Проверяем, что при запросе корневой ноды дерево возвращает само себя.
    """
    tree = NamedTree()

    assert tree is tree.search_node(['.'])

def test_put_node_one_level():
    """
    Пробуем вставить новую ноду первого уровня вложенности.
    """
    tree = NamedTree()
    tree['lol'] = 1
    tree['lol.kek'] = 1
    tree['lol.kek.cheburek'] = 1

    tree2 = NamedTree()
    tree2['lol'] = 1
    tree2['lol.kek'] = 1
    tree2['lol.kek.cheburek'] = 1

    tree.put_node('kek', tree2)

    assert len(tree) == 6

    assert 'kek' in tree
    assert 'lol' in tree
    assert 'kek.lol' in tree
