import pytest
from polog.core.stores.settings.setting_point import SettingPoint
from polog.errors import DoubleSettingError, AfterStartSettingError


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

def test_converter():
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

def test_change_once():
    """
    Проверка, что флаг "change_once" в значении True не дает изменить значение более 1 раза, а в положении False - позволяет.
    """
    point = SettingPoint('lol', change_once=True)
    point.set('kek')
    with pytest.raises(DoubleSettingError):
        point.set('cheburek')
    point = SettingPoint('lol', change_once=False)
    point.set('kek')
    point.set('cheburek')

def test_changed_flag():
    """
    Проверяем, что после первого изменения значения флаг "changed" выставляется в значение True.
    """
    point = SettingPoint('lol')
    assert point.changed == False
    point.set('kek')
    assert point.changed == True
    point.set('cheburek')
    assert point.changed == True

def test_set_after_start():
    """
    Проверяем работоспособность флага 'change_only_before_start' в 4 возможных комбинациях.
    """
    # 1.1 кейс - флаг 'started' в негативном положении, флаг 'change_only_before_start' тоже в негативном.
    # При изменении значения исключения быть не должно.
    store = {'started': False}
    point = SettingPoint('lol')
    point.set_store_object(store)
    point.set('kek')
    # 1.2 кейс - флаг 'started' в негативном положении, флаг 'change_only_before_start' тоже в негативном.
    # Разница с 1.1 - прописываем флаг 'change_only_before_start' в явном виде.
    # При изменении значения исключения быть не должно.
    store = {'started': False}
    point = SettingPoint('lol', change_only_before_start=False)
    point.set_store_object(store)
    point.set('kek')
    # 2 кейс - флаг 'started' в негативном положении, флаг 'change_only_before_start' в позитивном.
    # При изменении значения исключения быть не должно.
    store = {'started': False}
    point = SettingPoint('lol', change_only_before_start=True)
    point.set_store_object(store)
    point.set('kek')
    # 3 кейс - флаг 'started' в позитивном положении, флаг 'change_only_before_start' в негативном.
    # При изменении значения исключения быть не должно.
    store = {'started': True}
    point = SettingPoint('lol', change_only_before_start=False)
    point.set_store_object(store)
    point.set('kek')
    # 4 кейс - флаг 'started' в позитивном положении, флаг 'change_only_before_start' тоже в позитивном.
    # При изменении значения должно подняться исключение.
    store = {'started': True}
    point = SettingPoint('lol', change_only_before_start=True)
    point.set_store_object(store)
    with pytest.raises(AfterStartSettingError):
        point.set('kek')
