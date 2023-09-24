import pytest

from polog.core.stores.settings.actions.reload_engine import reload_engine
from polog import log
from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.engine.engine import Engine


def test_new_engine_generated(handler):
    """
    Проверяем, что при вызове reload_engine() объект real_engine заменяется.
    """
    log('kek')

    old_real_engine = Engine().real_engine

    reload_engine(1, 2, SettingsStore())

    new_real_engine = Engine().real_engine

    assert old_real_engine is not new_real_engine
