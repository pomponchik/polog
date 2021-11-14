import time
from threading import active_count

import pytest

from polog import log
from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.engine.real_engines.singlethreaded.engine import SingleThreadedRealEngine
from polog.core.engine.engine import Engine


def test_simple_behavior(handler):
    """
    Проверяем, что лог в принципе записывается.
    """
    settings = SettingsStore()
    settings['max_queue_size'] = 0
    settings['pool_size'] = 0

    log('kek')

    assert handler.last is not None

    settings['pool_size'] = 2

def test_change_engine(handler):
    """
    Проверяем, объект движка подменяется при манипуляциях с настройками.
    """
    settings = SettingsStore()
    engine_wrapper = Engine()

    settings['max_queue_size'] = 0
    settings['pool_size'] = 2

    log('kek')

    assert not isinstance(engine_wrapper.real_engine, SingleThreadedRealEngine)

    settings['pool_size'] = 0

    assert isinstance(engine_wrapper.real_engine, SingleThreadedRealEngine)

    settings['pool_size'] = 2

    assert not isinstance(engine_wrapper.real_engine, SingleThreadedRealEngine)
