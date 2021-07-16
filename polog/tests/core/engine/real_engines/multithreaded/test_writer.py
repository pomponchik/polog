import time
import pytest
from polog.core.engine.real_engines.multithreaded.writer import MultiThreadedRealEngine


def test_write_and_size():
    """
    Проверяем, что новые сообщения попадают в очередь.
    """
    time.sleep(0.0001)
    writer = MultiThreadedRealEngine({'started': True, 'pool_size': 2, 'delay_before_exit': 0.1})
    assert writer.queue_size() == 0
    writer.write(None, **{'lol': 'kek'})
    writer.write(None, **{'lol': 'kek'})
    assert writer.queue_size() == 2
