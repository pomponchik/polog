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
