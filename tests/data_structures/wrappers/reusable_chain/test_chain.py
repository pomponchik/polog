from polog.data_structures.wrappers.reusable_chain.chain import ReusableChain


def test_simple_chain():
    """
    Проверяем, что по нескольким итерабельным объектам можно итерироваться как по одному.
    Пробуем разные количества списков.
    """
    assert list(ReusableChain()) == []
    assert list(ReusableChain([])) == []
    assert list(ReusableChain([1, 2, 3])) == [1, 2, 3]
    assert list(ReusableChain([1, 2, 3], [4, 5, 6])) == [1, 2, 3, 4, 5, 6]
    assert list(ReusableChain([1, 2, 3], (4, 5, 6))) == [1, 2, 3, 4, 5, 6]
    assert list(ReusableChain([1, 2, 3], [4, 5, 6], [7, 8, 9])) == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_reusable_chain():
    """
    Проверяем собственно способность к переиспользованию итерабельных объектов.

    Итерируемся по паре списков дважды, это должно давать одинаковый результат (itertools.chain работает так, как здесь показано, только в первый раз).
    """
    chain = ReusableChain([1, 2, 3], [4, 5, 6])
    assert list(chain) == [1, 2, 3, 4, 5, 6]
    assert list(chain) == [1, 2, 3, 4, 5, 6]


def test_reusable_chain_with_adding_new_element():
    """
    Проверяем, что между итерациями можно добавить в один из итерабельных объектов новый элемент и при следующей итерации мы его увидим.

    Это значит, что переиспользование итерабельных объектов происходит не путем мемоизации (как например в случае itertools.tee).
    """
    lst_2 = [4, 5, 6]
    chain = ReusableChain([1, 2, 3], lst_2)
    assert list(chain) == [1, 2, 3, 4, 5, 6]
    lst_2.append(7)
    assert list(chain) == [1, 2, 3, 4, 5, 6, 7]


def test_reusable_chain_repr():
    """
    Проверяем, что repr у ReusableChain отображает его внутреннюю структуру.
    """
    assert repr(ReusableChain()) == 'ReusableChain()'
    assert repr(ReusableChain([1, 2, 3])) == 'ReusableChain([1, 2, 3])'
    assert repr(ReusableChain([1, 2, 3], [4, 5, 6])) == 'ReusableChain([1, 2, 3], [4, 5, 6])'
    assert repr(ReusableChain([1, 2, 3], (4, 5, 6))) == 'ReusableChain([1, 2, 3], (4, 5, 6))'
