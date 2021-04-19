import time
import pytest
from polog import log


def test_base_use(handler):
    handler.clean()
    log('kek')
    time.sleep(0.0001)
    assert handler.last['message'] == 'kek'
