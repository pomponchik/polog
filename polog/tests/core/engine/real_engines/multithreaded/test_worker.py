import time
from queue import Queue

import pytest

from polog.core.engine.real_engines.multithreaded.worker import Worker
from polog.core.stores.settings.settings_store import SettingsStore


queue = Queue()
worker = Worker(queue, 1, SettingsStore())


def test_do(handler):
    """
    Проверяем, что хендлер вызывается.
    """
    handler.clean()
    worker.do_anything({'lol': 'kek'})
    assert handler.last is not None
    worker.set_stop_flag()
    worker.stop()
