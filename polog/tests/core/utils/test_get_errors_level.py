import pytest

from polog.core.utils.get_errors_level import get_errors_level
from polog.core.stores.settings.settings_store import SettingsStore
from polog import config


def test_get_base_level():
    """
    Проверяем, что, если локальный уровень логирования в декораторе / функции не установлен, он берется из настроек.
    """
    assert get_errors_level(None) == SettingsStore()['errors_level']

def test_handle_level():
    """
    Проверяем, что, если локальный уровень логирования установлен, используется он.
    Также проверяем, что уровни логирования, указанные текстом, преобразуются в числа.
    """
    config.levels(lol=500)
    assert get_errors_level(500) == 500
    assert get_errors_level('lol') == 500

def test_error_level():
    """
    Если указать идентификатор уровня, ранее не зарегистрированный в Polog, вернуться должен стандартный уровень логирования для ошибок.
    То же самое должно произойти, если указать невозможный идентификатор уровня (в примере - отрицательный).
    """
    assert get_errors_level('lolkekololo') == SettingsStore()['errors_level']
    assert get_errors_level(-500) == SettingsStore()['errors_level']
