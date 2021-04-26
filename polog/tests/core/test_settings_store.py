import pytest
from polog.core.settings_store import SettingsStore


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
            'handlers': {},
            'extra_fields': {},
        },
        {
            'pool_size': 12,
            'original_exceptions': True,
            'level': 3,
            'service_name': 'kek',
            'errors_level': 12,
            'delay_before_exit': 3,
            'handlers': {},
            'extra_fields': {},
        },
    ]
    for values in all_values:
        for key, value in values.items():
            to_set = {key: value}
            SettingsStore(**to_set)
            assert getattr(SettingsStore, key) == value
