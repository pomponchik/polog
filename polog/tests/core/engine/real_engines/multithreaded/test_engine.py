import time
from threading import active_count
import pytest
from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.engine.real_engines.multithreaded.engine import MultiThreadedRealEngine


def test_write_and_size(settings_mock):
    """
    Проверяем, что новые сообщения попадают в очередь.
    """
    time.sleep(0.0001)
    engine = MultiThreadedRealEngine(settings_mock)
    assert engine.queue_size() == 0
    engine.write({'lol': 'kek'})
    engine.write({'lol': 'kek'})
    assert engine.queue_size() == 2
    engine.stop()

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

def test_lost_items_on_stop(settings_mock, handler):
    """
    Проверяем, что при остановке движка логи не теряются.
    """
    handler.clean()
    settings_mock.handlers['lol'] = handler
    engine = MultiThreadedRealEngine(settings_mock)

    number_of_items = 5000

    for index in range(number_of_items):
        engine.write({'lol': 'kek'})
    engine.stop()

    assert len(handler.all) == number_of_items

def test_get_size(settings_mock):
    """
    Проверяем, что счетчик числа элементов в очереди работает.
    """
    engine = MultiThreadedRealEngine(settings_mock)
    engine.write({'lol': 'kek'})
    assert engine.queue_size() == 1
    engine.write({'lol': 'kek'})
    assert engine.queue_size() == 2
    engine.stop()
