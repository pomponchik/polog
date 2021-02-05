import time
import pytest
from polog.core.writer import Writer


def test_singleton():
    """
    Проверяем, что Writer - это синглтон.
    """
    assert Writer() is Writer()

def test_write_and_size():
    """
    Проверяем, что новые сообщения попадают в очередь.
    """
    time.sleep(0.0001)
    writer = Writer()
    assert writer.queue_size() == 0
    writer.write(None, **{'lol': 'kek'})
    writer.write(None, **{'lol': 'kek'})
    assert writer.queue_size() == 2
