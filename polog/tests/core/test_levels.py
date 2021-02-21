import pytest
from polog.core.levels import Levels


def test_set_and_get():
    """
    Проверяем, что новые значения уровней по ключу устанавливаются, и потом считываются.
    """
    Levels.set('kek', 10000)
    assert Levels.get('kek') == 10000
    Levels.set('kek', 5)
    assert Levels.get('kek') == 5
