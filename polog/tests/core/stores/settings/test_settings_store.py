import pytest
from polog.core.stores.settings.settings_store import SettingsStore


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
            'delay_before_exit': 5,
        },
        {
            'pool_size': 12,
            'original_exceptions': True,
            'level': 3,
            'service_name': 'kek',
            'errors_level': 12,
            'delay_before_exit': 3,

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
        'delay_before_exit': ['kek', None, -1],
    }
    store = SettingsStore()
    for key, local_values in all_values.items():
        for value in local_values:
            with pytest.raises(ValueError):
                store[key] = value
