import pytest

from polog.core.utils.get_errors_level import get_errors_level
from polog.core.stores.settings.settings_store import SettingsStore
from polog import config


def test_get_base_level():
    """
    Проверяем, что, если локальные уровни логирования в декораторе / функции не установлены, результат берется из настроек.
    """
    config.set(default_error_level=500, default_level=5)

    assert get_errors_level(None, None) == SettingsStore()['default_error_level']

def test_handle_level():
    """
    Проверяем, что, если локальный уровень логирования для ошибок установлен, используется он.
    Также проверяем, что уровни логирования, указанные текстом, преобразуются в числа.
    """
    config.levels(lol=500)

    assert get_errors_level(500, None) == 500
    assert get_errors_level('lol', None) == 500

def test_error_level():
    """
    Если указать идентификатор уровня, ранее не зарегистрированный в Polog, вернуться должен стандартный уровень логирования для ошибок.
    То же самое должно произойти, если указать невозможный идентификатор уровня (в примере - отрицательный).
    """
    config.set(default_error_level=500, default_level=5)

    assert get_errors_level('lolkekololo', None) == SettingsStore()['default_error_level']
    assert get_errors_level(-500, None) == SettingsStore()['default_error_level']

def test_max_level_if_not_determined():
    """
    Если уровень логирования для ошибок не установлен, должен использоваться максимальный из трех: локальный уровень для обычных событий (не ошибок, если установлен), глобальный дефолтный уровень для обычных событий, глобальный дефолтный уровень для ошибок.
    Проверяем, что это так и работает.
    """
    config.set(default_error_level=500, default_level=5)

    assert get_errors_level(-5, 1000) == 1000
    assert get_errors_level(-5, 5) == SettingsStore()['default_error_level']

    config.set(default_level=700)

    assert get_errors_level(-5, 5) == SettingsStore()['default_level']
    assert get_errors_level(-5, -5) == SettingsStore()['default_level']
