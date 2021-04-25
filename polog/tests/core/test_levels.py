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

def test_set_and_get_raises():
    """
    Проверяем проверки типов данных для уровней логирования и их алиасов при их чтении / изменении.
    """
    with pytest.raises(KeyError):
        Levels.get(set()) # Пробуем использовать в качестве ключа объект с неподходящим типом данных.
    with pytest.raises(ValueError):
        Levels.set('lol', 'kek') # Пытаемся назначить алиас на алиас.
        # TODO: а почему бы, кстати, не разрешить так делать?
    with pytest.raises(KeyError):
        Levels.set(5, 'kek') # Алиас и числовое значение уровня перепутаны местами.

def test_get_int():
    """
    Проверяем, что в случае ключа-числа возвращается это же самое число.
    То есть уровень в данном случае равен самому себе.
    """
    assert Levels.get(5) == 5
    assert Levels.get(25) == 25

def test_reverse():
    """
    Назначаем одному и тому же уровню разные алиасы и проверяем, что в реверсах всегда "отпечатывается" последний.
    """
    Levels.set('kek', 777)
    assert Levels.levels_reverse[777] == 'kek'
    Levels.set('lol', 777)
    assert Levels.levels_reverse[777] == 'lol'

def test_get_level_name():
    """
    Проверка, аналогичная test_reverse(). Только для метода Levels.get_level_name().
    """
    Levels.set('kek', 777)
    assert Levels.get_level_name(777) == 'kek'
    Levels.set('lol', 777)
    assert Levels.get_level_name(777) == 'lol'

def test_add_get_all_names():
    """
    Добавляем новый алиас и проверяем, что он появляется в списке всех алиасов.
    """
    assert 'lolkeklolkek' not in Levels.get_all_names()
    Levels.set('lolkeklolkek', 777)
    assert 'lolkeklolkek' in Levels.get_all_names()

def test_get_level_name_none_request():
    """
    Проверяем, что если запросить имя уровня логирования передачей в качестве аргумента None - вернется None.
    """
    assert Levels.get_level_name(None) is None
