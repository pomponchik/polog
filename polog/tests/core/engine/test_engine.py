import time
from threading import active_count, Thread
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

def test_reload_missive_attack(handler):
    """
    Пробуем перезагрузить движок в тот момент, пока другой поток пишет логи.
    За счет блокировок ни одно событие не должно потеряться.
    """
    engine = Engine()
    store = SettingsStore()
    engine.write(None, **{'lol': 'kek'})
    handler.clean()

    number_of_items = 3000

    def go_attack():
        for x in range(number_of_items):
            engine.write((None, None), **{'lol': 'kek'})
    thread = Thread(target=go_attack)
    thread.start()

    engine.reload()
    time.sleep(0.1)

    assert len(handler.all) == number_of_items

    thread.join()
