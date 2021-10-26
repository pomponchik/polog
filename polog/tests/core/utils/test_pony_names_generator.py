import pytest

from polog.core.utils.pony_names_generator import PonyNamesGenerator


def test_new_portion_len():
    """
    Проверяем, что число комбинаций имен соответствует ожидаемому.
    Данное число == 7*7 + 5*5.
    """
    assert len(PonyNamesGenerator.new_names_portion()) == 74

def test_new_portion_contains():
    """
    Проверяем, что некоторые ожидаемые комбинации присутствуют.
    """
    assert 'Twilight Sparkle' in PonyNamesGenerator.new_names_portion()
    assert 'Pinkie Pie' in PonyNamesGenerator.new_names_portion()
    assert 'Pinkie Sparkle' in PonyNamesGenerator.new_names_portion()

def test_base_combinations():
    """
    Проверяем, что декартово произведение работает.
    """
    container = []
    PonyNamesGenerator.halfs_combinations(
        container,
        [
            'a',
            'b',
        ],
        [
            'a',
            'b',
        ],
    )
    assert container == ['aa', 'ab', 'ba', 'bb']

def test_prefix_combinations():
    """
    Проверяем, что декартово произведение работает и префиксы проставляются.
    """
    container = []
    PonyNamesGenerator.halfs_combinations(
        container,
        [
            'a',
            'b',
        ],
        [
            'a',
            'b',
        ],
        prefix='c',
    )
    assert container == ['caa', 'cab', 'cba', 'cbb']

def test_roman_numerals():
    """
    Проверяем генератор римских цифр.
    """
    assert PonyNamesGenerator.roman_numerals(1) == 'I'
    assert PonyNamesGenerator.roman_numerals(2) == 'II'
    assert PonyNamesGenerator.roman_numerals(5) == 'V'
    assert PonyNamesGenerator.roman_numerals(15) == 'XV'
    assert PonyNamesGenerator.roman_numerals(2134) == 'MMCXXXIV'
    assert PonyNamesGenerator.roman_numerals(0) is None
    assert PonyNamesGenerator.roman_numerals(-1) is None

def test_generator_works_10000():
    """
    Пробуем сгенерировать много имен и проверяем, что что-то генерируется.
    Также проверяем, что среди сгенерированных имен есть несколько из выборки.
    """
    names = []
    for index, x in enumerate(PonyNamesGenerator().get_next_pony()):
        assert len(x) > 0
        names.append(x)
        if index > 10000:
            break
    assert 'Pinkie Pie' in names
    assert 'Pinkie Pie II' in names
    assert 'Pinkie Pie I' not in names
