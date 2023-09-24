import time
from queue import Queue

import pytest

from polog.core.engine.real_engines.multithreaded.worker import Worker
from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.log_item import LogItem


queue = Queue()
worker = Worker(queue, 1, SettingsStore())


def test_do(handler):
    """
    Проверяем, что хендлер вызывается.
    """
    log = LogItem()
    log.set_handlers([handler])
    log.set_data({'lol': 'kek'})

    worker.do_anything(log)
    assert handler.last is not None

    worker.set_stop_flag()
    worker.stop()
