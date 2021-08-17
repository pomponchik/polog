import json
import pytest
from polog.core.stores.settings.settings_store import SettingsStore
import ujson


def test_set_and_get():
    """
    Проверяем, что параметры назначаются.
    """
    all_values = [
        {
            'pool_size': 7,
            'original_exceptions': False,
            'level': 5,
            'service_name': 'lol',
            'errors_level': 7,
            'max_delay_before_exit': 5,
        },
        {
            'pool_size': 12,
            'original_exceptions': True,
            'level': 3,
            'service_name': 'kek',
            'errors_level': 12,
            'max_delay_before_exit': 3,
        },
    ]
    store = SettingsStore()
    for values in all_values:
        for key, value in values.items():
            store[key] = value
            assert store[key] == value

def test_set_error_values():
    """
    Проверяем, что при попытке изменить значение параметра на невозможный поднимается исключение.
    """
    all_values = {
        'pool_size': [1.4, None, 'kek', -100],
        'original_exceptions': [None, 'no', 7, 1.5],
        'level': [1.2, None, -6],
        'service_name': [1.2, None],
        'errors_level': [1.2, None, -5],
        'max_delay_before_exit': ['kek', None, -1],
        'json_module': ['kek', 1, lambda x: 'kek'],
    }
    store = SettingsStore()
    for key, local_values in all_values.items():
        for value in local_values:
            with pytest.raises(ValueError):
                store[key] = value

def test_error_keys():
    """
    Проверяем, что при использовании неправильного ключа - поднимется KeyError.
    """
    store = SettingsStore()
    with pytest.raises(KeyError):
        value = store['lol']
    with pytest.raises(KeyError):
        store['lol'] = 'kek'

def test_share_lock_specific():
    """
    Проверяем, что между полями, где локи должны быть пошарены, они пошарены.
    """
    store = SettingsStore()
    assert store.get_point('pool_size').lock is store.get_point('max_queue_size').lock
    assert store.get_point('pool_size').lock is store.get_point('started').lock

def test_conflicts_specific():
    """
    Проверяем, что нельзя выставить ненулевой размер очереди, если у пула потоков размер 0.
    А также, что нельзя выставить пулу потоков нулевой размер, если очередь ненулевая.
    """
    store = SettingsStore()
    store['max_queue_size'] = 0
    store['pool_size'] = 0

    with pytest.raises(ValueError):
        store['max_queue_size'] = 1
    store['pool_size'] = 2
    store['max_queue_size'] = 1

    with pytest.raises(ValueError):
        store['pool_size'] = 0
    store['max_queue_size'] = 0
    store['pool_size'] = 0

    store['pool_size'] = 4

def test_set_json_module():
    """
    Пробуем зарегистрировать альтернативный модуль json.
    """
    store = SettingsStore()
    assert store['json_module'] is json
    store['json_module'] = ujson
    assert store['json_module'] is ujson
    store['json_module'] = json
    assert store['json_module'] is json
