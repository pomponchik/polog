import pytest

from polog import config
from polog.core.stores.settings.actions.set_log_as_built_in import set_log_as_built_in


def test_set_log_as_built_in_true(handler):
    """
    Проверяем, что если включить данную настройку, функция log() будет доступна как встроенная.
    """
    config.set(pool_size=0, level=0, default_level=5)
    set_log_as_built_in(False, True, {})

    log('kek')

    assert handler.last is not None
    assert handler.last['message'] == 'kek'

def test_set_log_as_built_in_false(handler):
    """
    Пробуем отключить данную настройку и проверяем, что функция log() перестает быть доступной.
    """
    config.set(pool_size=0, level=0, default_level=5)

    set_log_as_built_in(True, False, {})
    with pytest.raises(NameError):
        log('kek')
    assert handler.last is None

    set_log_as_built_in(False, True, {})
    log('kek')
    assert handler.last is not None
    handler.clean()

    set_log_as_built_in(True, False, {})
    with pytest.raises(NameError):
        log('kek')
    assert handler.last is None
