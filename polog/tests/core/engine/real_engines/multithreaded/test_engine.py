import time
from threading import active_count
import pytest
from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.engine.real_engines.multithreaded.engine import MultiThreadedRealEngine


def test_write_and_size():
    """
    Проверяем, что новые сообщения попадают в очередь.
    """
    time.sleep(0.0001)
    engine = MultiThreadedRealEngine({'started': True, 'pool_size': 2, 'delay_before_exit': 0.1, 'max_queue_size': 50, 'time_quant': 0.001})
    assert engine.queue_size() == 0
    engine.write(None, **{'lol': 'kek'})
    engine.write(None, **{'lol': 'kek'})
    assert engine.queue_size() == 2

def test_number_of_threads(handler):
    """
    Проверяем, что создании объекта движка потоки в нужном количестве создаются, а с вызовом метода stop() - уничтожаются.
    """
    store = SettingsStore()
    store['pool_size'] = 2
    before = active_count()
    engine = MultiThreadedRealEngine(store)
    after = active_count()
    assert after == before + store['pool_size']
    engine.stop()
    after = active_count()
    assert after == before
