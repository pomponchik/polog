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
    point.set_store_object({})

    assert point.get() == True
    point.set(False)
    assert point.get() == False
    point.set(True)
    assert point.get() == True

def test_set_new_value_with_prove():
    """
    Проверяем, что новое значение проверяется на валидность.
    """
    point = SettingPoint(True, proves={'prove': lambda x: x == False}, no_check_first_time=True)
    point.set_store_object({})

    point.set(False)
    assert point.get() == False
    with pytest.raises(ValueError):
        point.set(True)

def test_error_text():
    """
    Проверяем, что сообщение об ошибке при передаче неправильного значения содержит фразу, которая была использована как ключ в словаре.
    """
    prove_description = 'lol kek cheburek'
    point = SettingPoint(True, proves={prove_description: lambda x: x == False}, no_check_first_time=True)
    try:
        point.set(True)
    except ValueError as e:
        string_representation = str(e)
        assert prove_description in string_representation

def test_no_check_first_time():
    """
    Проверяем, что флаг "no_check_first_time" отменяет проверку дефолтного значения.
    """
    with pytest.raises(ValueError):
        point = SettingPoint(False, proves={'prove': lambda x: x == True})
    point = SettingPoint(False, proves={'prove': lambda x: x == True}, no_check_first_time=True)

def test_converter():
    """
    Проверяем, что конвертер по умолчанию не трогает дефолтное значение, но новые значения конвертит.
    Также проверяем, что проверки проходятся до того, как срабатывает конвертер.
    """
    point = SettingPoint('lol', converter=lambda x: 'kek', proves={'prove': lambda x: x != 'lolkek'})
    point.set_store_object({})

    assert point.get() == 'lol' # Проверка, что не подставилось значение из конвертера еще на этапе инициализации.
    with pytest.raises(ValueError):
        point.set('lolkek') # Проверяет, что проверка отрабатывает, хотя конвертер вывел бы значение из-под ее действия, если бы отработал до нее.
    point.set('keklol')
    assert point.get() == 'kek' # Проверяем, что подставилось значение из конвертера.

def test_converter_in_first_time_off():
    """
    Проверяем, что если параметр convert_first_time установлен в False, используется поведение по умолчанию.
    А именно - конвертация дефолтного значения не происходит (но последующие значения конвертируются).
    """
    point = SettingPoint('lol', converter=lambda x: 'kek', convert_first_time=False)
    point.set_store_object({})

    assert point.get() == 'lol'
    point.set('perekek')
    assert point.get() == 'kek'

def test_converter_in_first_time_on():
    """
    Проверяем, что если параметр convert_first_time установлен в True, дефолтный параметр сразу конвертируется.
    Последующие значения также конвертируются.
    """
    point = SettingPoint('lol', converter=lambda x: 'kek', convert_first_time=True)
    point.set_store_object({})

    assert point.get() == 'kek'
    point.set('perekek')
    assert point.get() == 'kek'

def test_change_once():
    """
    Проверка, что флаг "change_once" в значении True не дает изменить значение более 1 раза, а в положении False - позволяет.
    """
    point = SettingPoint('lol', change_once=True)
    point.set_store_object({})

    point.set('kek')
    with pytest.raises(DoubleSettingError):
        point.set('cheburek')

    point = SettingPoint('lol', change_once=False)
    point.set_store_object({})

    point.set('kek')
    point.set('cheburek')

def test_changed_flag():
    """
    Проверяем, что после первого изменения значения флаг "changed" выставляется в значение True.
    """
    point = SettingPoint('lol')
    point.set_store_object({})

    assert point.changed == False
    point.set('kek')
    assert point.changed == True
    point.set('cheburek')
    assert point.changed == True

def test_set_changet_flag_after_error():
    """
    Проверяем, что при откате значения (если оно не прошло проверку) флаг "changed" не изменяется.
    """
    point = SettingPoint('lol', proves={'lol': lambda x: x != 'kek'})
    point.set_store_object({})

    with pytest.raises(ValueError):
        point.set('kek')

    assert not point.changed

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

def test_share_lock():
    """
    Проверяем, что объекты блокировок действительно шарятся.
    """
    class PseudoStore:
        points = {'point_1': SettingPoint('lol'), 'point_2': SettingPoint('kek', shared_lock_with=('point_1', )), 'point_3': SettingPoint('cheburek')}
        def __init__(self):
            for name, point in self.points.items():
                point.set_store_object(self)
                point.set_name(name)
            for name, point in self.points.items():
                point.share_lock_object()
        def __getitem__(self, key):
            return self.get_point(key).get()
        def get_point(self, key):
            return self.points.get(key)

    store = PseudoStore()

    assert store.get_point('point_1').lock is store.get_point('point_2').lock
    assert store.get_point('point_1').lock is not store.get_point('point_3').lock

def test_conflicts():
    """
    Проверяем, что конфликты срабатывают как ожидалось.
    """
    class PseudoStore:
        points = {
            'point_1': SettingPoint('lol'),
            'point_2': SettingPoint('kek', conflicts={
                'point_1': lambda new_value, old_value, other_field_value: other_field_value == 'lol'
            }),
            'point_3': SettingPoint('cheburek', conflicts={
                'point_1': lambda new_value, old_value, other_field_value: new_value == old_value + '_kek'
            })
        }
        def __init__(self):
            for name, point in self.points.items():
                point.set_store_object(self)
                point.set_name(name)
            for name, point in self.points.items():
                point.share_lock_object()
        def __getitem__(self, key):
            return self.get_point(key).get()
        def __setitem__(self, key, value):
            self.get_point(key).set(value)
        def get_point(self, key):
            return self.points.get(key)
        def force_get(self, key):
            return self[key]

    store = PseudoStore()

    with pytest.raises(ValueError):
        store['point_2'] = 'lolkek'

    store['point_1'] = 'lolkek'
    store['point_2'] = 'lolkek'

    with pytest.raises(ValueError):
        store['point_3'] = 'cheburek_kek'

    store['point_3'] = 'lolkek'

def test_run_callback_when_setting_changes():
    """
    Проверяем, что в нормальных условиях (когда новое значение корректно и принимается) установленный коллбек - вызывается.
    """
    kek = 0
    def callback(a, b, c):
        nonlocal kek
        kek = 1

    point = SettingPoint('lol', action=callback)
    point.set_store_object({})
    point.set('kek')

    assert kek == 1

def test_run_callback_when_setting_no_changes():
    """
    Проверяем, что если новое значение не принимается, то коллбек вызван не будет.
    """
    kek = 0
    def callback(a, b, c):
        nonlocal kek
        kek = 1

    point = SettingPoint('lol', action=callback, proves={'lol': lambda x: x != 'kek'})
    point.set_store_object({})

    with pytest.raises(ValueError):
        point.set('kek')

    assert kek == 0
