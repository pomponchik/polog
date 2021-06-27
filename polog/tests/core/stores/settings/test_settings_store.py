import pytest
from polog.core.stores.settings.settings_store import SettingsStore


def test_set_and_get():
    """
    Проверяем, что назначение новых параметров через .__init__() работает.
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
