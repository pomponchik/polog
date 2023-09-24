import gc

import pytest

from polog.data_structures.wrappers.weak_linked.dictionary import LockedWeakKeyValueDictionary


class HandleHashed:
    def __init__(self, hash):
        self.hash = hash
    def __hash__(self):
        return self.hash
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.hash == other.hash
    def __repr__(self):
        return f'{type(self).__name__}({self.hash})'
    def __str__(self):
        return repr(self)

def test_creating_without_arguments():
    """
    Просто проверяем, что без аргументов создается объект словаря.
    """
    container = LockedWeakKeyValueDictionary()

    assert len(container) == 0

def test_add_and_len(empty_class):
    """
    Проверяем, что если добавить сколько-то элементов в словарь, то длина словаря изменяется соответствующе.
    """
    container = LockedWeakKeyValueDictionary()

    # Все ключи и значения складываются в список, чтобы на них оставались действующие ссылки.
    links = []
    for index in range(100):
        key = HandleHashed(index)
        links.append(key)
        container[key] = key
        assert len(container) == index + 1

    assert len(container) == 100

def test_set_and_get():
    """
    Пробуем класть в словарь объекты и доставать их оттуда.
    """
    container = LockedWeakKeyValueDictionary()

    links = []
    for index in range(100):
        key = HandleHashed(index)
        links.append(key)
        container[key] = key
        assert container[key] == key

def test_set_and_del():
    """
    Кладем в словарь объекты и удаляем их при помощи директивы del.
    Проверяем, что они действительно удаляются.
    """
    container = LockedWeakKeyValueDictionary()

    links = []
    for index in range(100):
        key = HandleHashed(index)
        links.append(key)
        container[key] = key
        del container[key]

        assert len(container) == 0
        assert container.get(key) is None
        with pytest.raises(KeyError):
            container[key]

def test_del_empty():
    """
    Пробуем удалить ключ, которого в словаре нет.
    Должно подняться исключение.
    """
    container = LockedWeakKeyValueDictionary()

    with pytest.raises(KeyError):
        del container[HandleHashed(0)]

def test_set_and_iterate_keys():
    """
    Пробуем сохранить в словаре данные, после чего проитерироваться по ключам при помощи метода .keys().
    """
    container = LockedWeakKeyValueDictionary()

    links = []
    for index in range(100):
        key = HandleHashed(index)
        links.append(key)
        container[key] = HandleHashed(index * 1000)

    for key, second_key in zip(links, container.keys()):
        assert key == second_key

def test_set_and_iterate_it():
    """
    Пробуем сохранить в словаре данные, после чего проитерироваться по нему.
    Итерирование должно произойти именно по ключам (не по значениям).
    """
    container = LockedWeakKeyValueDictionary()

    links = []
    for index in range(100):
        key = HandleHashed(index)
        links.append(key)
        container[key] = HandleHashed(index * 1000)

    for key, second_key in zip(links, container):
        assert key == second_key

def test_set_and_iterate_values():
    """
    Пробуем сохранить в словаре данные, после чего проитерироваться по значениям в нем.
    """
    container = LockedWeakKeyValueDictionary()

    values = []
    keys = []
    for index in range(100):
        key = HandleHashed(index)
        value = HandleHashed(index * 1000)
        keys.append(key)
        values.append(value)
        container[key] = value

    for value, second_value in zip(values, container.values()):
        assert value == second_value

def test_pop_empty_without_default():
    """
    Пробуем удалить элемент из пустого словаря при помощи метода .pop(), не задавая дефолтное значение для возврата.
    Должно подняться KeyError.
    """
    container = LockedWeakKeyValueDictionary()

    with pytest.raises(KeyError):
        container.pop(HandleHashed(0))

def test_pop_empty_with_default():
    """
    Пробуем удалить элемент из пустого словаря при помощи метода .pop(), задав дефолтное значение.
    Дефолтное значение должно вернуться.
    """
    container = LockedWeakKeyValueDictionary()

    assert 'kek' == container.pop(HandleHashed(0), 'kek')

def test_pop_empty_with_default_none():
    """
    Пробуем удалить элемент из пустого словаря при помощи метода .pop(), задав дефолтное значение None.
    Дефолтное значение должно вернуться.
    """
    container = LockedWeakKeyValueDictionary()

    assert container.pop(HandleHashed(0), None) is None

def test_pop_not_empty_with_default():
    """
    Пробуем удалить элемент из словаря при помощи метода .pop(), предварительно заполнив его по удаляемому ключу.
    Должно вернуться значение по ключу.
    """
    container = LockedWeakKeyValueDictionary()

    key = HandleHashed(0)
    value = HandleHashed(1)
    container[key] = value

    assert HandleHashed(1) == container.pop(key, 'kek')
    assert HandleHashed(1) != 'kek'

def test_pop_not_empty_without_default():
    """
    Пробуем удалить элемент из словаря при помощи метода .pop(), предварительно заполнив его по удаляемому ключу.
    Должно вернуться значение по ключу.
    """
    container = LockedWeakKeyValueDictionary()

    key = HandleHashed(0)
    value = HandleHashed(1)
    container[key] = value

    assert HandleHashed(1) == container.pop(key)

def test_not_hashable():
    """
    Проверяем, что словарь не является хэшируемым, как в пустом виде, так и заполненный.
    """
    container = LockedWeakKeyValueDictionary()

    with pytest.raises(TypeError):
        hash(container)

    key = HandleHashed(0)
    value = HandleHashed(1)
    container[key] = value

    with pytest.raises(TypeError):
        hash(container)

def test_set_none_as_key():
    """
    Пробуем сохранить в словаре значение по ключу в виде None.
    """
    container = LockedWeakKeyValueDictionary()

    key = None
    value = HandleHashed(1)

    with pytest.raises(TypeError):
        container[key] = value

def test_set_none_as_value():
    """
    Пробуем сохранить в словаре None как значение.
    """
    container = LockedWeakKeyValueDictionary()

    key = HandleHashed(0)
    value = None

    with pytest.raises(TypeError):
        container[key] = value

def test_auto_cleaning_by_keys():
    """
    Пробуем сохранять в словаре значения, после чего сразу удалять использованные в качестве ключей переменные.
    Из словаря соответствующее содержимое также должно удаляться.
    """
    container = LockedWeakKeyValueDictionary()

    for index in range(100):
        key = HandleHashed(index)
        value = HandleHashed(index * 1000)
        container[key] = value
        del key

    assert len(container) == 0

def test_auto_cleaning_by_values():
    """
    Пробуем сохранять в словаре значения, после чего сразу удалять использованные в их качестве переменные.
    Из словаря соответствующее содержимое также должно удаляться.
    """
    container = LockedWeakKeyValueDictionary()

    for index in range(100):
        key = HandleHashed(index)
        value = HandleHashed(index * 1000)
        container[key] = value
        del value

    assert len(container) == 0

def test_str_text_representation_of_the_locked_weak_key_value_dictionary():
    """
    Проверяем, что функция str() возвращает правильную строковую репрезентацию словаря.
    """
    container = LockedWeakKeyValueDictionary()

    assert str(container) == '<LockedWeakKeyValueDictionary object (empty)>'

    key = HandleHashed(0)
    value = HandleHashed(1)
    container[key] = value

    assert str(container) == '<LockedWeakKeyValueDictionary object with data: {HandleHashed(0): HandleHashed(1)}>'

def test_locked_weak_key_value_dictionary_contains():
    """
    Проверяем, что оператор in работает.
    """
    container = LockedWeakKeyValueDictionary()

    assert (HandleHashed(0) in container) == False

    key = HandleHashed(0)
    value = HandleHashed(1)
    container[key] = value

    assert (HandleHashed(0) in container) == True
