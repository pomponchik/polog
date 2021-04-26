import time
from queue import Queue
import pytest
from polog.core.worker import Worker


queue = Queue()
worker = Worker(queue, 1)


def test_do(handler):
    """
    Проверяем, что хендлер вызывается.
    """
    handler.clean()
    worker.do_anything((None, None), **{'lol': 'kek'})
    assert handler.last is not None
