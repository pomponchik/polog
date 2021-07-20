from threading import active_count
import pytest
from polog.core.engine.engine import Engine
from polog.core.stores.settings.settings_store import SettingsStore


def test_singleton():
    """
    Проверяем, что Writer - это синглтон.
    """
    assert Engine() is Engine()

def test_reload_threads_counting():
    """
    Проверяем, что количество потоков увеличивается в соответствии с ожидаемым увеличением пула потоков при перезагрузке движка.
    """
    engine = Engine()
    store = SettingsStore()
    engine.write(None, **{'lol': 'kek'})

    before = active_count()
    store['pool_size'] = store['pool_size'] + 2
    engine.reload()
    after = active_count()

    assert after == before + 2
