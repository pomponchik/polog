from polog.data_structures.wrappers.reusable_map.map import ReusableMap


def test_reusable_map_simple_using():
    """
    Проверяем, что ReusableMap вообще работает, и делает это так же, как оригинальный map.
    """
    assert list(ReusableMap(lambda x: x * 2, [1, 2, 3])) == [2, 4, 6]


def test_reusable_map_double_using():
    """
    Проверяем, что ReusableMap собственно является переиспользуемым, то есть по нему можно проитерироваться более одного раза.

    Обычный map во втором assert'е дал бы пустой список, то есть он не является переиспользуемым.
    """
    reusable_map = ReusableMap(lambda x: x * 2, [1, 2, 3])

    assert list(reusable_map) == [2, 4, 6]
    assert list(reusable_map) == [2, 4, 6]


def test_reusable_map_changing_and_double_using():
    """
    Проверяем, что между проходами по списку в него можно добавить новый элемент, после чего тот обработается при новом проходе.

    Это бы не работало, если бы ReusableMap работал на основе мемоизации, то есть мы по сути проверяем, что мемоизация тут не используется.
    """
    lst = [1, 2, 3]
    reusable_map = ReusableMap(lambda x: x * 2, lst)

    assert list(reusable_map) == [2, 4, 6]
    assert list(reusable_map) == [2, 4, 6]

    lst.append(4)

    assert list(reusable_map) == [2, 4, 6, 8]


def test_reusable_map_repr():
    """
    Проверяем, что текстовая репрезентация объекта работает как надо.
    """
    assert repr(ReusableMap(lambda x: x, [1, 2, 3])).startswith('ReusableMap(')
    assert repr(ReusableMap(lambda x: x, [1, 2, 3])).endswith(', [1, 2, 3])')
