import pytest
from polog.core.stores.settings.setting_point import SettingPoint


def test_create_base_point():
    """
    Проверяем, что пункт настроек создается в своей минимальной форме, и сохраняет в себе дефолтное значение.
    """
    point = SettingPoint(True)
    assert point.get() == True

def test_set_new_value_without_prove():
    """
    Проверяем, что новое значение устанавливается, при условии, что не указаны никакие проверки.
    """
    point = SettingPoint(True)
    assert point.get() == True
    point.set(False)
    assert point.get() == False
    point.set(True)
    assert point.get() == True

def test_set_new_value_with_prove():
    """
    Проверяем, что новое значение проверяется на валидность.
    """
    point = SettingPoint(True, prove=lambda x: x == False, no_check_first_time=True)
    point.set(False)
    assert point.get() == False
    with pytest.raises(ValueError):
        point.set(True)

def test_no_check_first_time():
    """
    Проверяем, что флаг "no_check_first_time" отменяет проверку дефолтного значения.
    """
    with pytest.raises(ValueError):
        point = SettingPoint(False, prove=lambda x: x == True)
    point = SettingPoint(False, prove=lambda x: x == True, no_check_first_time=True)

def test_converter_default():
    """
    Проверяем, что конвертер не трогает дефолтное значение, но новые значения конвертит.
    Также проверяем, что проверки проходятся до того, как срабатывает конвертер.
    """
    point = SettingPoint('lol', converter=lambda x: 'kek', prove=lambda x: x != 'lolkek')
    assert point.get() == 'lol' # Проверка, что не подставилось значение из конвертера еще на этапе инициализации.
    with pytest.raises(ValueError):
        point.set('lolkek') # Проверяет, что проверка отрабатывает, хотя конвертер вывел бы значение из-под ее действия, если бы отработал до нее.
    point.set('keklol')
    assert point.get() == 'kek' # Проверяем, что подставилось значение из конвертера.
