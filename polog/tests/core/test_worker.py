import time
from queue import Queue
import pytest
from polog.core.worker import Worker
from polog import config
from polog.handlers.memory.saver import memory_saver


queue = Queue()
worker = Worker(queue, 1)
handler = memory_saver()
config.add_handlers(handler)

def test_do():
    """
    Проверяем, что хендлер вызывается.
    """
    handler.clean()
    worker.do_anything((None, None), **{'lol': 'kek'})
    assert handler.last is not None
