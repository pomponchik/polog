import time
import pytest
from polog.handlers.smtp.sender import SMTP_sender
from polog import log, config


lst = []

class DependencyWrapper:
    def __init__(self, v1, v2, v3, v4, v5):
        pass

    def send(self, message):
        lst.append(message)

config.add_handlers(SMTP_sender('fff', 'fff', 'fff', 'fff', smtp_wrapper=DependencyWrapper))


def test_send_normal():
    log('hello')
    time.sleep(0.0001)
    assert lst[0]
    lst.pop()
